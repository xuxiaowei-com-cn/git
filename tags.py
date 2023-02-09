import os

import requests

# 获取 https://api.github.com/repos/git/git/tags 最新30个标签的 URL
tags_url = 'https://api.github.com/repos/git/git/tags'
# 从环境变量中获取参数
num = os.getenv("num")
print(f'num={num}')
page = os.getenv("page")
print(f'page={page}')

if num is not None:
    num = int(num)
if page is not None:
    page = int(page)
    tags_url += f'?page={page}'

resp = requests.get(tags_url)

resp_json = resp.json()

file_name = 'tags.sh'
if os.path.exists(file_name):
    os.remove(file_name)

file = open(file_name, 'w')

i = 0
for tag in resp_json:
    i = i + 1
    dockerfile_name = f'Dockerfile{i}'
    file.write(f"wget https://github.com/git/git/archive/refs/tags/{tag['name']}.tar.gz\n")
    file.write(f"cp {dockerfile_name} Dockerfile\n")
    file.write(f"docker build -t $DOCKER_USERNAME/git:{tag['name']} .\n")
    file.write("docker images\n")

    if os.path.exists(dockerfile_name):
        os.remove(dockerfile_name)
    dockerfile = open(dockerfile_name, 'w')

    dockerfile.write(f"""
        # 第一阶段：编译 git 源码

        # 选择运行时基础镜像
        FROM openanolis/anolisos:8.6 as git-make
        
        # 维护人员
        MAINTAINER 徐晓伟 xuxiaowei@xuxiaowei.com.cn
        
        # 工作空间
        WORKDIR /home/git
        
        # 添加 git 源码
        ADD {tag['name']}.tar.gz .
        
        # 查看文件
        RUN ls
        
        # 调整工作空间
        WORKDIR /home/git/git-{tag['name'][1:]}
        
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
        RUN make DESTDIR=/git-{tag['name']} install
        
        # 执行编译安装后的可执行文件
        RUN /git-{tag['name']}/root/bin/git --version
        
        
        # 第二阶段，使用第一阶段编译构建好的可执行文件来构建 git 镜像
        
        FROM openanolis/anolisos:8.6
        
        WORKDIR /home
        
        # 从第一阶段中复制构建好的可执行文件
        COPY --from=git-make /git-{tag['name']}/root/bin/ /usr/bin/
        COPY --from=git-make /git-{tag['name']}/root/libexec/ /usr/libexec/
        COPY --from=git-make /git-{tag['name']}/root/share/ /usr/share/
        
        RUN git --version

    """)
    if num is not None and i >= num:
        break
