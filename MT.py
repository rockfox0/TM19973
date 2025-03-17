from randcrack import randcrack, RandCrack
from copy import deepcopy, copy


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
        a=deepcopy(mt[623])
        c=deepcopy(mt[396])
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
def re_tw1(mt):
    high=0x80000000
    low=0x7fffffff
    mask=0x9908b0df
    for i in range(623,-1,-1):
        t=mt[i]^mt[(i+397) % 624]
        if t&high==high:
            t=t^mask
            t=t<<1
            t|=1#确定位奇数
        else:
            t=t<<1
        res=t&high #取得高位
        t=mt[i-1]^mt[(i+396) % 624]
        if t&high==high:
            t=t^mask
            t=t<<1
            t|=1
        else:
            t=t<<1
        res=res+(t&low)
        mt[i]=res
    return mt
if __name__ == '__main__':
    M1 = []
    M2 = []
    rng = MT19937(seed=1123)
    for i in range(1248):
        a = rng.extract_number()
        if i < 624:
            M1.append(a)
        else:
            M2.append(a)
    print(f'M1={M1}')
    print(f'M2={M2}')
    pre = MT19937()
    m = pre.re_state(M2)
    pre.mt=re_tw1(m)
    print(f'pre.mt={pre.mt}')
    print("预测 RNG:", [pre.extract_number(x=1) for _ in range(10)])
