def get_register_bin(str):
    str = str.replace(str[0], "", 1)
    dec=int(str)
    if (dec<0 or dec>15): return "ValueError"
    return bin(dec)[2:].zfill(4)

def bins_to_hex(str):
    return '%0*X' % ((len(str) + 3) // 4, int(str, 2))

def get_immediate_bin_unsigned6bits(str):
    dec=int(str)
    if(dec < 0 or dec > 63): return "ValueError"
    return bin(dec)[2:].zfill(6)

def get_immediate_bin_signed6bits(str):
    dec=int(str)
    if(dec > 31 or dec < -32): return "ValueError"
    if dec < 0:
        dec_complement = dec % (1 << 6)
    else:
        dec_complement = dec
    binary_str = format(dec_complement, f'0{6}b')
    return binary_str

def get_immediate_bin_10(str):
    dec=int(str)
    if(dec < 0 or dec > 1023): return "ValueError"
    return bin(dec)[2:].zfill(10)

def get_immediate_bin_9(str):
    dec=int(str)
    if(dec < 0 or dec > 511): return "ValueError"
    return bin(dec)[2:].zfill(9)

def get_address_bin_signed13bit(str):
    dec=int(str)
    if (dec > 4095 or dec < -4096):
        return "ValueError"
    if dec < 0:
        dec_complement = dec % (1 << 13)
    else:
        dec_complement = dec
    binary_str = format(dec_complement, f'0{13}b')
    return binary_str

def get_address_bin_unsigned10bit(str):
    dec=int(str)
    if (dec > 1023 or dec < -1024):
        return "ValueError"
    return bin(dec)[2:].zfill(10)

#group1: op reg1 reg2 reg3
def group1(words):
    r1=get_register_bin(words[1])
    r2=get_register_bin(words[2])
    r3=get_register_bin(words[3])
    if (r1=="ValueError" or r2=="ValueError" or r3=="ValueError"):
        return "ValueError"
    
    match words[0]:
        case "add":
            opcode="0000"
            func="00"
        case "sub":
            opcode="0000"
            func="01"
        case "nand":
            opcode="0000"
            func="10"
        case "nor":
            opcode="0000"
            func="11"
        case "srl":
            opcode="0001"
            func="00"
        case "sra":
            opcode="0001"
            func="01"
        case "cmov":
            opcode="0001"
            func="10"
        
    bins="00"+opcode+r1+r2+func+r3
    return bins_to_hex(bins)

#group2: op reg1 reg2 imm
def group2(words):
    r1=get_register_bin(words[1])
    r2=get_register_bin(words[2])
    
    match words[0]:
        case "addi":
            imm=get_immediate_bin_unsigned6bits(words[3])
            opcode="0011"
        case "subi":
            imm=get_immediate_bin_unsigned6bits(words[3])
            opcode="0100"
        case "nandi":
            imm=get_immediate_bin_signed6bits(words[3])
            opcode="0101"
        case "nori":
            imm=get_immediate_bin_signed6bits(words[3])
            opcode="0110"
        
    if (r1=="ValueError" or r2=="ValueError"):
        return "RegValueError"
    elif(imm=="ValueError"):
        return "ImmValueError"

    bins="00"+opcode+r1+r2+imm
    return bins_to_hex(bins)    

#group4: op reg
def group4(words):
    r=get_register_bin(words[1])
    if (r=="ValueError"):
        return "ValueError"
    
    match words[0]:
        case "pop":
            opcode="1110"
            func="000010"
        case "push":
            opcode="1110"
            func="000011"
        
    bins="00"+opcode+"0000"+func+r
    return bins_to_hex(bins)

#group5: op addr(13 bits)(signed)
def group5(words):
    addr=get_address_bin_signed13bit(words[1])
    if(addr=="ValueError"):
        return "ValueError"
    
    match words[0]:
        case "jump":
            opcode="0010"
            func="0"
        case "jal":
            opcode="0010"
            func="1"

    bins="00"+opcode+func+addr
    return bins_to_hex(bins)

#group6: op reg addr(10)(unsigned)
def group6(words):
    r=get_register_bin(words[1])
    addr=get_address_bin_unsigned10bit(words[2])
    if(r=="ValueError"):
        return "RegValueError"
    elif(addr=="ValueError"):
        return "AddrValueError"

    match words[0]:
        case "ld":
            opcode="0111"
        case "st":
            opcode="1000"

    bins="00"+opcode+r+addr
    return bins_to_hex(bins)

newlinecount=0
err=0
code=open('code.asm','r')
binf=open('bin.raw','w')
output="v2.0 raw\n"
content=(code.readlines())
i=0
j=0
for line in content:
    j+=1
    i+=1
    line=(line.lower()).replace(","," ")
    words=line.split()
    hexstr=""
    if not words:
        i-=1
        continue
    match words[0]:
        #group1: op reg1 reg2 reg3
        case "add" | "sub" | "nand" | "nor" | "srl" | "sra" | "cmov":
            hexstr=group1(words)
            if(hexstr=="ValueError"):
                print("Register value out of range on line "+str(j))
                err=1
            else: output+=(hexstr+" ")
        #group2: op reg1 reg2 imm
        case "addi"| "subi" | "nandi" | "nori":
            hexstr=group2(words)
            if(hexstr=="RegValueError"):
                print("Register value out of range on line "+str(j))
                err=1
            elif(hexstr=="ImmValueError"):
                print("Immediate value out of range on line "+str(j))
                err=1
            else: output+=(hexstr+" ")
        #group4: op reg
        case "pop" | "push":
            hexstr=group4(words)
            if(hexstr=="ValueError"):
                print("Register value out of range on line "+str(j))
                err=1
            else: output+=(hexstr+" ")
        #group5: op addr
        case "jump" | "jal":
            hexstr=group5(words)
            if(hexstr=="ValueError"):
                print("Address value out of range on line "+str(j))
                err=1
            else: output+=(hexstr+" ")
        #group6: op reg addr
        case "ld" | "st":
            hexstr=group6(words)
            if(hexstr=="AddrValueError"):
                print("Address value out of range on line "+str(j))
                err=1
            elif(hexstr=="RegValueError"):
                print("Register value out of range on line "+str(j))
                err=1
            else: output+=(hexstr+" ")
        case "lui":
            r=get_register_bin(words[1])
            imm=get_immediate_bin_9(words[2])
            if(r=="ValueError"):
                print("Register value out of range on line "+str(j))
                err=1
            elif(imm=="ValueError"):
                print("Immediate value out of range on line "+str(j))
                err=1
            else:
                hexstr=bins_to_hex("001001"+r+"0"+imm)
                output+=(hexstr+" ")
        case _ if words[0].startswith("//"):
            i-=1
        case _:
            print("No match for instruction "+words[0]+" on line "+str(j))
    if (i%6==0 and newlinecount<i/6):
        newlinecount+=1
        output+=("\n")
if err==0:
    binf.write(output)
else:
    print("Program terminated with syntax errors")



    