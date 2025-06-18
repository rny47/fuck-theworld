# 环境部署
## 系统基础软件包
> 因各个系统不同，安装方法不同，请自行搜索安装方法

- `git`
- `wget`
- `openjdk-23`
- `p7zip`
- `python3.13`
- [ ] `andriod build-tools` 可用版本待确定
- [ ] `andriod cmdline-tools` 可用版本待确定

## `apktool`
- `jar`包
去[官网](https://apktool.org/)下载最新版
> 目前最新版本 `apktool_2.11.1.jar `

- `shell`脚本
```shell
wget https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool
```

- 将`jar`包和`shell`脚本放到同一个目录并给可执行权限
```shell
chmod +x apktool && chmod +x apktool_2.11.1.jar && \
mv apktool /usr/bin && mv apktool_2.11.1.jar /usr/bin
```

## `AndResGuard`

### 下载源代码
```shell
git clone https://github.com/shwenzhang/AndResGuard.git

cd AndResGuard
```

### 修改打包配置
#### `build.gradle`

```shell
vi build.gradle
```

```gradle
// Top-level build file where you can add configuration options common to all sub-projects/modules.
buildscript {
  repositories {
    google()
    jcenter()
  }
  dependencies {
    classpath 'com.android.tools.build:gradle:4.1.2'
    //classpath 'com.jfrog.bintray.gradle:gradle-bintray-plugin:1.8.4'
    //classpath 'com.ofg:uptodate-gradle-plugin:1.6.2'
  }
}

allprojects {
  repositories {
    google()
    jcenter()
  }
  tasks.withType(JavaCompile) {
    sourceCompatibility = rootProject.ext.javaVersion
    targetCompatibility = rootProject.ext.javaVersion
  }

  tasks.withType(GroovyCompile) {
    sourceCompatibility = rootProject.ext.javaVersion
    targetCompatibility = rootProject.ext.javaVersion
  }
}

ext {
  javaVersion = JavaVersion.VERSION_1_8

  GROUP = 'com.tencent.mm'
  VERSION_NAME = "${ANDRESGUARD_VESSION}"

  POM_PACKAGING = "pom"
  POM_DESCRIPTION = "Android Resource Proguard Core Lib"

  POM_URL = "https://github.com/shwenzhang/AndResGuard"
  POM_SCM_URL = "https://github.com/shwenzhang/AndResGuard.git"
  POM_ISSUE_URL = 'https://github.com/shwenzhang/AndResGuard/issues'

  POM_LICENCE_NAME = "Apache-2.0"
  POM_LICENCE_URL = " http://www.apache.org/licenses/"
  POM_LICENCE_DIST = "repo"

  POM_DEVELOPER_ID = "Tencent Wechat"
  POM_DEVELOPER_NAME = "Tencent Wechat, Inc."

  BINTRAY_LICENCE = ["Apache-2.0"]
  BINTRAY_ORGANIZATION = "wemobiledev"
}
```

#### `gradle/gradle-mvn-push.gradle`

```shell
vi gradle/gradle-mvn-push.gradle
```

```gradle
apply plugin: 'maven'
//apply plugin: 'com.jfrog.bintray'

def getBintrayUser() {
  return hasProperty('BINTRAY_USER') ? BINTRAY_USER :
      readPropertyFromLocalProperties('BINTRAY_USER')
}

def getBintrayKey() {
  return hasProperty('BINTRAY_APIKEY') ? BINTRAY_APIKEY :
      readPropertyFromLocalProperties('BINTRAY_APIKEY')
}

def readPropertyFromLocalProperties(String key) {
  Properties properties = new Properties()
  try {
    properties.load(project.rootProject.file('local.properties').newDataInputStream())
  } catch (Exception ignore) {
  }
  return properties.getProperty(key)
}
//
// bintray {
//   user = getBintrayUser()
//   key = getBintrayKey()
//   configurations = ['archives']
//   publications = ['ResguardPub']
//
//   pkg {
//     repo = 'maven'
//     userOrg = BINTRAY_ORGANIZATION
//     name = "${GROUP}:${POM_ARTIFACT_ID}"
//     desc = POM_DESCRIPTION
//     licenses = BINTRAY_LICENCE
//     vcsUrl = POM_SCM_URL
//     websiteUrl = POM_URL
//     issueTrackerUrl = POM_ISSUE_URL
//     publicDownloadNumbers = true
//     publish = true
//     dryRun = false
//   }
// }



task buildAndPublishRepo(dependsOn: ['build', 'uploadArchives']) {
  doLast {
    println "*published to repo: ${project.group}:${project.name}:${project.version}"
  }
}

```

#### `AndResGuard-cli/build.gradle`
  
```shell
vi AndResGuard-cli/build.gradle
```

```gradle
buildscript {
    repositories {
        gradlePluginPortal()
        mavenCentral()
        google()
    }
    dependencies {
        classpath 'com.github.jengelman.gradle.plugins:shadow:2.0.4'
    }
}

apply plugin: 'java'
apply plugin: 'com.github.johnrengelman.shadow'

group = 'com.tencent.mm'
version = '1.2.21'

repositories {
    mavenCentral()
    google()
}

dependencies {
    implementation project(":AndResGuard-core")
    compile fileTree(dir: 'libs', include: ['*.jar'])
    compile project(':AndResGuard-core')
}

shadowJar {
    archiveName = 'AndResGuard-cli-1.2.21-all.jar' // 旧版写法
    exclude 'META-INF/*.SF'
    exclude 'META-INF/*.RSA'
    exclude 'META-INF/*.DSA'
}

[compileJava, compileTestJava, javadoc]*.options*.encoding = 'UTF-8'

jar {
    manifest {
        attributes(
            'Main-Class': 'com.tencent.mm.resourceproguard.cli.CliMain',
            'Manifest-Version': version,
            'Jar-Version': "${ANDRESGUARD_VESSION}",
            'Build-Time': releaseTime()
        )
    }
    from {
        configurations.compile.collect { it.isDirectory() ? it : zipTree(it) }
    }
    exclude 'META-INF/*.SF'
    exclude 'META-INF/*.RSA'
    exclude 'META-INF/*.DSA'
}

task buildJar(type: Copy, dependsOn: ['build', 'jar']) {
    from('build/libs') {
        include "*${version}*.jar"
    }
    into('../tool_output')
}

def releaseTime() {
    return new Date().format("yyyy-MM-dd HH:mm ZZZ", TimeZone.getDefault())
}

defaultTasks 'buildJar'
```

#### 编译jar包
```shell
./gradlew :AndResGuard-cli:shadowJar
```

编译好之后，能找到下面的`jar`包

```shell
ls AndResGuard-cli/build/libs/AndResGuard-cli-1.2.21-all.jar 

# 测试执行
java -jar AndResGuard-cli/build/libs/AndResGuard-cli-1.2.21-all.jar 
```

**讲编译出来的jar包放到一个合适的位置备用**

# 流程测试
## `apk`原包解包
```shell
apktool d -f -o /path/to/decompiled/dir /path/to/orin.apk
```
> 解包后进入解包目录 

## 对`AndroidManifest.xml`文件的修改
### 包名
1. 在 `AndroidManifest.xml` 文件中找到原始报名 `xml`文件的`package`域
2. 如果需要修改报名，新包名和原始报名的段（以`.`分割）数必须一致。_不知道为啥要这样_

### 随机化一些域的值
- `android:compileSdkVersion`
- `android:compileSdkVersionCodename`
- `android:sharedUserId`
  - 这个如果不存在的话，会新增
- `platformBuildVersionCode`
- `platformBuildVersionName`
- `android:initOrder`
  - 每个子域名递归新增

## 对`.smali` 文件注入垃圾代码
> smali 文件是 Android 应用中的一种中间代码格式文件，它是 Dalvik 字节码的可读/可写文本表示形式，主要在反编译和修改 APK 时出现。
**`.smali`文件存在`smali*`目录中，可能有多个**

1. 对`AndroidManifest.xml`中，下列域对应的`.smali`混入垃圾代码。如:域中`android:name`的值为`com.gobal.h5.base.BaseApplication`,则对应的`.smali`文件的下级路径为`com/gobal/h5/base/BaseApplication`
  - `application`
  - `activity`
  - `service`
  - `provider`
  - `receiver`
2. 找寻其他的`.smali`文件，混入垃圾代码

## 对`.xml`文件的处理(不包含`AndroidManifest.xml`)
1. 混入垃圾`xml`域
2. 随机化各个域的顺序

## 对`png`图片文件进行处理
批量地在一个文件夹内的所有 PNG 图片上，随机选取一个像素点，并对其颜色稍作修改（变亮或变暗），然后保存覆盖原图。
这种做法常用于：
- 对抗图像指纹检测/内容指纹（比如规避 hash-based 的相似图检测）
- 轻量图像扰动，用于测试模型鲁棒性
- 防止简单图像比较算法发现一致性
- 或者加点扰动做 watermark 类伪加密

## 精简包的体积
如果存在`lib`目录，优先保留 lib/armeabi-v7a 而后 lib/arm64-v8a，去除多余的 arm 架构。

## 重新打包
```shell
apktool b -o /path/to/new.apk /path/to/decompiled/dir
```

## 加固签名`apk`包

加固使用到这个工具（可选）
- `AndResGuard`
- `Jiagu-Pack-1.0-SNAPSHOT.jar`(这个不知道哪里来的)
- `zipalign`
签名(也是可选，有些加固工具自带签名)
- `apksigner`


# 新方案选型
- [ ] `androguard`(`python`模块)
- [ ] `redex`(`facebook`开发)

