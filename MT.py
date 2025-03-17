from randcrack import randcrack, RandCrack


def _int32(x):
    return int(0xFFFFFFFF & x)

class MT19937:
    def __init__(self, seed=None):
        self.mt = [0] * 624
        self.mt[0] = seed
        self.mti = 0
        if seed is not None:
            self.seed_mt(seed)
    def seed_mt(self,seed):
        self.mt[0]=_int32(seed)
        for i in range(1, 624):
            self.mt[i] = _int32(1812433253 * (self.mt[i - 1] ^ self.mt[i - 1] >> 30) + i)

    def extract_number(self,x=None):
        if self.mti == 0 and x is None:
            self.twist()
        y = self.mt[self.mti]
        y = y ^ y >> 11
        y = y ^ y << 7 & 2636928640
        y = y ^ y << 15 & 4022730752
        y = y ^ y >> 18
        self.mti = (self.mti + 1) % 624
        return _int32(y)


    def twist(self):
        for i in range(0, 624):
            y = _int32((self.mt[i] & 0x80000000) + (self.mt[(i + 1) % 624] & 0x7fffffff))
            self.mt[i] = (y >> 1)

            if y % 2 != 0:
                self.mt[i] = self.mt[i] ^ 0x9908b0df
            self.mt[i]^=self.mt[(i + 397) % 624]
    def re_right(self,x,bit,mask=0xffffffff):
        tmp=x
        for _ in range(32//bit):
            tmp=x^tmp>>bit&mask
        return tmp

    def re_left(self, x, bit, mask=0xffffffff):
        tmp = x
        for _ in range(32 // bit):
            tmp = x ^ tmp << bit & mask
        return tmp

    def re_extract(self,m):
        m=self.re_right(m,18,0xffffffff)
        m=self.re_left(m,15,4022730752)
        m=self.re_left(m,7,2636928640)
        m=self.re_right(m,11)
        return m&0xffffffff
    def re_state(self,outputs):
        if len(outputs)!=624:
            raise ValueError("Invalid number of outputs")

        self.mt=[self.re_extract(m)for m in outputs]
        self.mti=0
        return self.mt
    def re_twist(self,mt):
        re_tw=[0]*624#生成列表
        for i in range(623,-1,-1):#从大到小遍历，以便twist[(i+397)%624]是符合条件的
            k=mt[i]^mt[(i+397) % 624]
            if (k&0x80000000)>>31==1:#判断y>>1的第一位
                k=k^0x9908b0df
                low=1
                high=(k&0x40000000)>>30
                re_tw[i]=high<<31
                re_tw[(i+1)%624]=re_tw[(i+1)%624]+((k&0x3fffffff)<<1)+low
                if i !=623:
                    mt[(i+1)%624]=re_tw[(i+1)%624]#还原正确的依赖
            elif (k & 0x80000000) >> 31 == 0:
                low = 0
                high = (k & 0x40000000) >> 30
                re_tw[i] = high << 31
                re_tw[(i + 1) % 624] = re_tw[(i + 1) % 624] + ((k & 0x3fffffff) << 1) + low
                if i != 623:
                    mt[(i + 1) % 624] = re_tw[(i + 1) % 624]

        return re_tw

if __name__ == '__main__':
    def extract(mt):
        M=[]
        for y in mt:
            y = y ^ y >> 11
            y = y ^ y << 7 & 2636928640
            y = y ^ y << 15 & 4022730752
            y = y ^ y >> 18
            M.append(y)
        return M
    seed = 1123
    # 初始化 MT19937 生成器
    rng = MT19937(seed)
    M1, M2 = [], []
    # 提取 1248 个随机数，前 624 个存入 M1，后 624 个存入 M2
    for i in range(1248):
        num = rng.extract_number()
        if i < 624:
            M1.append(num)
        else:
            M2.append(num)
    print("M1:", M1)
    print("M2:", M2)


    pre = MT19937()
    state = pre.re_state(M2)
    recovered_state = pre.re_twist(state)
    pre.mt = pre.re_state(M1)
    print(recovered_state)
    print(pre.mt)
    M_1 = [pre.extract_number() for _ in range(624)]
    print("Recovered M1:", M_1)
