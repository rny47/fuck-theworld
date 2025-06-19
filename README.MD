## 安卓防爆毒 Python 项目部署

## 一、系统环境

<br />

### 1. 依赖说明

---

<br />

**需要安装的依赖**： `7zip`、`python 3.10.12`、`java-11`、 `apktool`、`commandlinetools`

```shell
# 7zip 安装方法示例
linux-ubuntu : sudo apt-get install p7zip-full
linux-centos : yum install p7zip
mac : brew install p7zip
# 7zip 验证： 执行 7za 可以打印使用帮助信息
7za
```

<br />

### 2. 环境安装

---

升级 openssl 到 1.1.1 (编译python3.10需要)，参考 https://computingforgeeks.com/how-to-install-openssl-1-1-on-centos-rhel-7/

> 安装 python3.10.12

```shell
wget https://www.python.org/ftp/python/3.10.12/Python-3.10.12.tar.xz
tar xf Python-3.10.12.tar.xz
cd Python-3.10.12
./configure --with-openssl=/usr/local/openssl
make
make install
```

<br />

> 安装： java-11

```shell
yum install java-11-openjdk-devel
# 运行命令检查安装是否正确
java -version
keytool
jarsigner
```

> 安装： apktool

```shell
wget https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool
wget https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.8.1.jar
mv apktool_2.8.1.jar apktool.jar
chmod +x apktool
chmod +x apktool.jar
chown www apktool
chown www apktool.jar
mv apktool /usr/local/bin/
mv apktool.jar /usr/local/bin/
```

> 安装：`commandlinetools`

```shell
wget https://dl.google.com/android/repository/commandlinetools-linux-10406996_latest.zip
unzip commandlinetools-linux-10406996_latest.zip
mv cmdline-tools /usr/local/android-sdk

cat > /etc/profile.d/android-sdk.sh <<'EOF'
export  PATH=$PATH:/usr/local/android-sdk/bin
EOF

source /etc/profile.d/android-sdk.sh
```


> 安装： `android build-tools 30.0.2`

```shell
wget https://dl.google.com/android/repository/build-tools_r30.0.1-linux.zip
unzip build-tools_r30.0.1-linux.zip
mv android-11 /usr/local/android-11

# 一定要修改权限，否则普通用户无法调用，比如PHP 进程用户
chmod -R 755 /usr/local/android-11

cat > /etc/profile.d/android-11.sh <<'EOF'
export  PATH=$PATH:/usr/local/android-11
EOF

source /etc/profile.d/android-11.sh

```

<br />

## 二、项目环境

<br />

### 1. 使用说明

---

<br />

**分支信息说明**：

- 分支 main：正式服使用分支 不包含加固壳；
- 分支 main-shell：正式服使用分支 包含加固壳；
- 分支 test：测试服使用分支；

加固壳是类似于360加固的壳子，可隐藏app的实际代码。
无论是否加壳，执行的命令参数都是相同的。

<br />

```shell
# 每次更新代码后需要执行一次依赖更新命令，满足项目中用到的三方库依赖
$ pip install -r requirements.txt     # 安装或更新依赖
```

<br />

### 2. 使用方法

------

<br />

```shell
# 使用示例：该示例在本项目根目录下运行
$ python bin/clean.py \
    --original-apk-path tests/apks/qubo-com.l7b1a70e74.f9726cf5b6.apk \
    --target-apk-path ~/Downloads/qubo-com.l7b1a70e74.f9726cf5b6.apk \
    --need-shrink true \
    --need-change-package-name true \
    --new-package-name com.live888.livequbo
```

<br />

- 注意：若要指定包名，则段数必须与原包名段数相同，否则运行时会报错
  - 如： `com.example.test` => `com.example.cast` (正确)
  - 如： `com.example.test` => `com.exa.ple.cast` (错误)
- 未标注 [required] 的参数为可选项
- 标注有 [default]  的参数表示不传时所使用的默认值
- 日志输出：正常执行的情况下不会有日志输出，出现错误时会有日志输出
- `--new-package-name`：若未指定新包名则不要写该选项。不可以传 Null None 等，因为这些会被作为字符串传入

<br />

```shell
$ python bin/clean.py --help    # 打印使用帮助

Usage: clean.py [OPTIONS]

  一步完成 apk 清理，可在任意位置执行该命令。注意：若要指定包名，则段数必须与原包名段数相同，否则运行时会报错

Options:
  --original-apk-path PATH            原始包路径，可以是相对路径或绝对路径  [required]
  --target-apk-path PATH              生成目标包路径，可以是相对路径或绝对路径  [required]
  --need-shrink BOOLEAN               是否需要压缩 apk，开启可能会有兼容性问题  [default: True]
  --need-change-package-name BOOLEAN  是否需要修改包名，不开启则使用原包名  [default: True]
  --new-package-name TEXT             当开启包名修改时：若需要修改包名，可以指定一个固定的包名，不指定则会使用随机包名
  --help                              Show this message and exit.


```

### 更新说明
- 本项目已使用 Python 实现 resguard.py 和 packager.py，完全替代 AndResGuard 与 Jiagu-Pack jar 工具。
