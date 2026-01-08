#include <SPI.h>

// Pin definitions
#define ADF4351_LE   10
#define ADF4351_CLK  13
#define ADF4351_DATA 11
#define ADF4351_CE   9
#define ADF4351_LD   8

// Global variables
uint32_t current_frequency = 50000000UL;  // Default to 50MHz
bool sweep_mode = false;

// Constants
const uint32_t REF_FREQ = 25000000UL;  // 25MHz reference
const uint32_t CHANNEL_SPACING = 100000UL;  // 100kHz

// Function declarations
void writeADF4351(uint32_t value);
uint32_t calculateR0(uint32_t freq_hz);
void setFrequency(uint32_t freq_hz);

// Register array with corrected values for 50MHz default
uint32_t registers[6] = {
    0x00780000,  // R0: Will be calculated based on frequency
    0x08008011,  // R1: Reference settings (25MHz), INT-N mode
    0x00004E42,  // R2: Low noise mode, reduced current
    0x000004B3,  // R3: Output divider will be calculated
    0x00EC803C,  // R4: RF output enable, +5dBm
    0x00580005   // R5: LD pin mode
};

void writeADF4351(uint32_t value) {
    digitalWrite(ADF4351_LE, LOW);
    delayMicroseconds(1);
    
    for (int i = 3; i >= 0; i--) {
        byte b = (value >> (8 * i)) & 0xFF;
        SPI.transfer(b);
    }
    
    delayMicroseconds(1);
    digitalWrite(ADF4351_LE, HIGH);
    delayMicroseconds(2);
    digitalWrite(ADF4351_LE, LOW);
}

uint32_t calculateR0(uint32_t freq_hz) {
    uint32_t divider;
    // Select output divider based on frequency range
    if (freq_hz < 68750000UL) divider = 64;
    else if (freq_hz < 137500000UL) divider = 32;
    else if (freq_hz < 275000000UL) divider = 16;
    else if (freq_hz < 550000000UL) divider = 8;
    else if (freq_hz < 1100000000UL) divider = 4;
    else if (freq_hz < 2200000000UL) divider = 2;
    else divider = 1;

    // Calculate VCO frequency
    uint32_t vco_freq = freq_hz * divider;
    
    // Calculate INT value
    uint32_t INT = vco_freq / REF_FREQ;
    
    // Debug output
    Serial.print(F("DEBUG: Target Freq (Hz): "));
    Serial.println(freq_hz);
    Serial.print(F("DEBUG: VCO Freq (Hz): "));
    Serial.println(vco_freq);
    Serial.print(F("DEBUG: Divider: "));
    Serial.println(divider);
    Serial.print(F("DEBUG: INT: "));
    Serial.println(INT);
    
    // Update output divider in R3
    uint32_t div_bits;
    switch(divider) {
        case 1: div_bits = 0; break;
        case 2: div_bits = 1; break;
        case 4: div_bits = 2; break;
        case 8: div_bits = 3; break;
        case 16: div_bits = 4; break;
        case 32: div_bits = 5; break;
        case 64: div_bits = 6; break;
        default: div_bits = 4; break;  // Default to 16
    }
    registers[4] = (registers[4] & ~(7UL << 20)) | (div_bits << 20);
    
    // Construct R0 register value
    uint32_t r0 = 0;
    r0 |= 0UL;              // Control bits
    r0 |= (INT << 15);      // Integer value
    r0 |= 0UL << 3;         // Fractional value (0 for integer-N mode)
    r0 |= 0UL;              // Register select (R0)
    
    return r0;
}

void setFrequency(uint32_t freq_hz) {
    if (freq_hz >= 35000000UL && freq_hz <= 4400000000UL) {
        current_frequency = freq_hz;
        
        // Calculate and set registers
        registers[0] = calculateR0(freq_hz);
        
        // Write all registers in reverse order
        for (int i = 5; i >= 0; i--) {
            writeADF4351(registers[i]);
            delay(1);
        }
        
        // Write R0 again for frequency update
        writeADF4351(registers[0]);
        
        // Verify lock status
        delay(10);
        bool locked = digitalRead(ADF4351_LD);
        Serial.print(F("DEBUG: PLL Lock Status: "));
        Serial.println(locked ? "Locked" : "Unlocked");
        
        Serial.println(F("OK"));
    } else {
        Serial.println(F("ERROR: Frequency out of range"));
    }
}

void setupADF4351() {
    pinMode(ADF4351_LE, OUTPUT);
    pinMode(ADF4351_CE, OUTPUT);
    pinMode(ADF4351_LD, INPUT);
    
    digitalWrite(ADF4351_LE, HIGH);
    
    // Power up sequence
    digitalWrite(ADF4351_CE, LOW);
    delay(10);
    digitalWrite(ADF4351_CE, HIGH);
    delay(10);
    
    SPI.begin();
    SPI.setBitOrder(MSBFIRST);
    SPI.setDataMode(SPI_MODE0);
    SPI.setClockDivider(SPI_CLOCK_DIV8);
    
    // Program all registers with initial values
    for (int i = 5; i >= 0; i--) {
        writeADF4351(registers[i]);
        delay(1);
    }
    
    // Set default frequency (50MHz)
    setFrequency(90000000UL);
}

void setup() {
    Serial.begin(115200);
    while (!Serial) {
        ; // Wait for serial port to connect
    }
    setupADF4351();
    Serial.println(F("ADF4351 RF Generator Ready"));
    Serial.println(F("Default frequency set to 50 MHz"));
}

void loop() {
    if (Serial.available()) {
        String cmd = Serial.readStringUntil('\n');
        cmd.trim();
        
        if (cmd.startsWith("FREQ:")) {
            float freq_mhz = cmd.substring(5).toFloat();
            uint32_t freq_hz = (uint32_t)(freq_mhz * 1000000UL);
            Serial.print(F("Setting frequency to "));
            Serial.print(freq_mhz);
            Serial.println(F(" MHz"));
            setFrequency(freq_hz);
        }
        else if (cmd == "STATUS") {
            Serial.print(F("Frequency: "));
            Serial.print(current_frequency / 1000000.0, 3);
            Serial.println(F(" MHz"));
            Serial.print(F("Lock Status: "));
            Serial.println(digitalRead(ADF4351_LD) ? "Locked" : "Unlocked");
        }
    }
}
// A Project By Akash Chohan