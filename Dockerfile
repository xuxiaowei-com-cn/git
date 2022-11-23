# 第一阶段：编译 git 源码

# 选择运行时基础镜像
FROM openanolis/anolisos:8.6 as git-make

# 维护人员
MAINTAINER 徐晓伟 xuxiaowei@xuxiaowei.com.cn

# 工作空间
WORKDIR /home/git

# 添加 git 源码
ADD v2.38.1.tar.gz .

# 查看文件
RUN ls

# 调整工作空间
WORKDIR /home/git/git-2.38.1

# 查看文件
RUN ls

# 以下软件如果不执行安装，会报出安装命令前类似注释中的错误

# /bin/sh: make: command not found
RUN yum -y install make
# /bin/sh: cc: command not found
RUN yum -y install gcc
# include <openssl/ssl.h>
RUN yum -y install openssl-devel
# include <curl/curl.h>
RUN yum -y install curl-devel
# include <expat.h>
RUN yum -y install expat-devel
# tclsh failed; using unoptimized loading
RUN yum -y install tcl-devel
# /bin/sh: msgfmt: command not found
RUN yum -y install gettext
# /bin/sh: cmp: command not found
RUN yum -y install diffutils

# 编译
RUN make
# 编译安装到指定的文件夹下
RUN make DESTDIR=/git-2.38.1 install

# 执行编译安装后的可执行文件
RUN /git-2.38.1/root/bin/git --version


# 第二阶段，使用第一阶段编译构建好的可执行文件来构建 git 镜像

FROM openanolis/anolisos:8.6

WORKDIR /home

# 从第一阶段中复制构建好的可执行文件
COPY --from=git-make /git-2.38.1/root/bin/ /usr/bin/
COPY --from=git-make /git-2.38.1/root/libexec/ /usr/libexec/
COPY --from=git-make /git-2.38.1/root/share/ /usr/share/

RUN git --version
