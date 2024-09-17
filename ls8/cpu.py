"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0
        self.ram = [0] * 256
        self.reg = [0] * 8
        # flag status
        self.FL = 0b00000000

     # MAR - Memory Address Register
    def ram_read(self, MAR):
        return self.ram[MAR]

    # MDR - Memory Data Register
    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def load(self, file):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        program = []

        try:
            with open(file) as f:
                for line in f:
                    instruction = line.split("#", 1)[0].strip()
                    if len(instruction):
                        program.append(int(instruction, 2))

            for instruction in program:
                self.ram[address] = instruction
                address += 1

        except FileNotFoundError:
            print(f"{sys.argv[0]}: {sys.argv[1]} not found")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            # FL bits: 00000LGE
            # L Less-than: during a CMP, set to 1 if registerA is less than registerB, zero otherwise.
            # G Greater-than: during a CMP, set to 1 if registerA is greater than registerB, zero otherwise.
            # E Equal: during a CMP, set to 1 if registerA is equal to registerB, zero otherwise.

            diff = self.reg[reg_a] - self.reg[reg_b]

            if diff == 0:
                self.FL = 0b00000001

            elif diff < 0:
                self.FL = 0b00000100

            elif diff > 0:
                self.FL = 0b00000010

            else:
                self.FL = 0b00000000
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()
    
    def ram_print(self):
        print(self.ram)

    def run(self):
        """Run the CPU."""
        # print(self.ram)
        running = True
        while running:
            current = self.ram[self.pc]
            opt_a = self.ram[self.pc + 1]
            opt_b = self.ram[self.pc + 2]
            if current == 0b00000001:  # HLT - Halt
                running = False
                self.pc += 1

            elif current == 0b10000010:  # LDI - Set value of a register to an int
                self.reg[opt_a] = opt_b
                self.pc += 3

            elif current == 0b01000111:  # PRN - Print register value
                print(self.reg[opt_a])
                self.pc += 2

            elif current == 0b10100010:            # MUL - Multiply 2 numbers
                self.alu("MUL", opt_a, opt_b)
                self.pc += 3

            elif current == 0b10100111:            # CMP - Compare register 0 and register 1 to see if Less/Greater/Equal
                self.alu("CMP", opt_a, opt_b)
                self.pc += 3

            elif current == 0b01010101:            # JEQ - 
                if self.FL == 0b00000001:
                    reg_n = self.ram[self.pc+1]
                    val = self.reg[reg_n]
                    self.pc = val
                else:
                    self.pc += 2
            
            elif current == 0b01010110:            # JNE - 
                if self.FL == 0b00000000:
                    reg_n = self.ram[self.pc+1]
                    self.pc = self.reg[reg_n]
                else:
                    self.pc += 2
        
            elif current == 0b01010100:            # JMP - 
                reg_n = self.ram[self.pc+1]
                self.pc = self.reg[reg_n]

            else:
                print(f'Unknown command {curr_reg}')
                sys.exit(1)
