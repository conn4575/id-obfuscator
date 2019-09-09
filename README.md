id obfuscator
====
这是一个将数字(通常是数据库的主键 ID)混淆为另一个看起来毫无规律的简短的数字或者字符串的库，并且可以将混淆后的内容再次还原回来。这个库主要受到了 Optimus 和 hashids 两个库的启发，结合了两者的一些特性。

## 为什么需要 id 混淆
使用数据库的自增长 ID 作为资源的唯一标识是非常普遍的场景，在设计 Rest 接口时，经常需要使用这个 ID 来获取指定的资源，例如通过 /user/{uid} 接口来获取用户信息，但是这样把数据库的 ID 直接暴露有很多问题：
* 爬虫可以很容易地爬取网站的用户信息
* 可以通过这个 ID 大致看出网站的用户规模

因此，通常情况下我们会在数据表里增加一行来记录一个随机且唯一字符串类型的 key，然后将这个 key 透出给前端。前端访问接口时传入这个 key，后端使用这个 key 从数据库查出数字 ID，再使用 ID 进行业务处理。

这种方式由的弊端：
* 这些 key 的实际作用和 ID 几乎一样的，相同作用的字段数据库存了两份。
* 这些 key 通常需要使用数据库的唯一索引来保证唯一，如果是已经做了分库分表或者使用了分布式的数据库，那么需要额外的逻辑来保证这个 key 的唯一。
* 如果初期设计数据库没有考虑到，后期像往数据库新增一列这样的 key 存在一定的风险，很多时候线上环境根本无法做这样的操作。

使用这个库，你可以非常轻松的将任何一个数字转化为另一个唯一的、非连续的数字或者字符串，而且无需额外的存储。同时，前端将这个混淆后的字符串传回来的时候，可以反解析出原来的 id。

## 写在前面
注意，这个库仅仅是作为一种简单的将数字混淆的方案，不是真正的加密算法，不要将它用在安全性要求很高的场景里，在这种场景里，你还是应该在数据库插入一个唯一的 key 来保证安全。

## 安装

## Getting Started
```python
from id_obfuscator import IntObfuscator, StrObfuscator

# 混淆为数字
obfuscator = IntObfuscator(2647619789, 4120924286, size=32)
obfuscated = obfuscator.encode(123456789)
print(obfuscated)  # output: 1409302959
i = obfuscator.decode(obfuscated)
print(i)  # output: 123456789

# 混淆为字符串
obfuscator = StrObfuscator(2647619789, 4120924286, 'ZoB2iHVWXPUEmxYgzJ8LSjekun5lt0DM7bhd4AvcGO6y3aR9rQNq1TpKfICFsw', size=32)
obfuscated = obfuscator.encode(123456789)
print(obfuscated)  # output: KTNUiFo
i = obfuscator.decode(obfuscated)
print(i)  # output: 123456789
```


## 用法
### IntObfuscator
`IntObfuscator` 的原理是利用了 Knuth 的乘法哈希法（Knuth's multiplicative hashing method）来实现可逆的整数混淆。`IntObfuscator` 初始化时需要三个参数：
* prime：一个比较大的素数，虽然实际上任何正素数都可以，但是这个数的大小和混淆效果关系密切，如果你的混淆目标是 32 位以内的所有正整数，推荐这个素数应该也是 32 位或者 31 位的。
* salt_int：一个整数盐值，它的位数也应该和你要混淆的位数基本一致
* size: 要混淆的数字的最大位数，默认是 32，prime、salt_int以及需要混淆的数字的位数都不能超过这个值，否者会报 ValueError。

> 注：不要直接使用 demo 里给出的素数和盐值，你应该自己提供一个组，并且保证不同业务使用的初始值是不一样的。
> 后面提供了一个命令行工具可以快速生成一组合适的初始值。

假如你取的 size=32，`IntObfuscator` 可以保证任何 32 位以内的正整数（零除外）都可以转化为另一个32 位以内的整数（包括零在内），也就说任何 32 位的整数都可以被反解析出另一个正整数作为它的混淆前的值，它是一个"可逆函数"。

### StrObfuscator
`StrObfuscator` 借鉴了 hashids 的部分思想，它会先使用`IntObfuscator`将传入的数字混淆为另一个数字，然后再使用指定的字符集将这个数字编码为一个字符串。  
`StrObfuscator`需要 4 个参数，
* prime、salt_int、size 和`IntObfuscator`一样，不再解释
* alphabet: 可参与混淆的字母表，注意，你不应该使用类似于 'abcdefg' 这样的有序字母表，而是应该将它们打乱后再传给 alphabet。

相比于`IntObfuscator`，`StrObfuscator`有一个非常有用的特性，它生成的混淆字符具有一定的自校验性。  
不是所有的字符串都可以反解析出一个有效的数字出来。只有那些通过`encode`方法得到的混淆字符才能反解析出原始的数字 id，其他字符串几乎都会被校验失败（此时返回值为 None）。虽然不能保证 100%，但是绝大多数情况下这个结论都是成立的。这个特性对防爬虫很有用，你几乎不需要查询数据库就可以判断出那些非法的key。

### FixedLengthStrObfuscator
`FixedLengthStrObfuscator`继承自`StrObfuscator`，它可以保证混淆后的字符串都有固定的长度。初始化使额外多了可选参数：
* fixed_length：混淆字符的固定长度，一般情况下可以不设置，初始化是会根据`size`和`alphabet`自动计算出能够覆盖`size`位数以内的所有整数所需要的最小字符长度。确保你自己设置的最小长度不能小于这个最小值，初始化时程序会检查这一点。
* padding_alphabet：用于补齐长度的字符集，这个参数也是可选的，默认情况下会从`alphabet`里面挑选 `ceil(len(alphabet)/12)`个字符作为 `padding_alphabet`, 例如，如果 size=32，alphabet=base62，那么将从这 62 个字符里选出 6 个作为 padding 字符，剩余的 56 个字符用于混淆，此时最小固定长度为 7。


## 命令行工具
为了方便的得到一组合适的初始值，我写了一个命令行工具，你只需要执行以下命令：
```
> python -m id_obfuscator.command spark
            
Bit length: 32
Prime: 2647619789
Salt_int: 4120924286
Alphabet: ZoB2iHVWXPUEmxYgzJ8LSjekun5lt0DM7bhd4AvcGO6y3aR9rQNq1TpKfICFsw
```
可选参数：
```
> python -m id_obfuscator.command spark --help
Usage: command.py spark [OPTIONS]

  生成一组给混淆器需要的随机初始参数

Options:
  -b, --bit INTEGER               混淆算法需要支持的最大数的位数
  -B, --base [base62|base64|readable47|lowercase|uppercase|lowercase36|uppercase36]
                                  使用内置的字母表
  --alphabet TEXT                 可用的字母表，默认使用 base62
  --help                          Show this message and exit.

```
其中，内置字母表有以下几种：
* base62：大写+小写+数字，默认值
* base64：url 安全的 base64 字符，在 base62 的基础上多了 `-` 和 `_` 两个字母
* readable47：更易阅读的字母表，在 base62 的基础上去掉了一些容易被认错的字母（`iI1sSzZ2oO0vVwW`），剩下 47 个字母
* lowercase： 全小写字母
* uppercase： 全大写字母
* lowercase36： 全小写+数字
* uppercase36： 全大写+数字
