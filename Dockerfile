#FROM ubuntu:20.04
#
#RUN apt-get update && \
#    apt-get install -y vim wget curl git zsh cmake gcc g++
#
## need manual install
##RUN apt-get install -y libgl1 libglib2.0-0 libsm6 libxrender1 libxext6
#
## install conda
#RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh \
#    && bash /tmp/miniconda.sh -b -p /opt/conda \
#    && rm /tmp/miniconda.sh
#ENV PATH="/opt/conda/bin:$PATH"
#
## set zsh and oh-my-zsh
#RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
#RUN chsh -s $(which zsh)
#
#RUN conda init zsh
#RUN conda create -n ManiRender python=3.8
#
#WORKDIR /ManiRender
#COPY . /ManiRender
#
#CMD ["/bin/zsh"]


FROM yanghece96/manirender

COPY . /ManiRender