FROM gitpod/workspace-full:latest

# Install gq
ENV PATH="$PATH:$HOME/node_modules/.bin"
RUN npm install graphqurl@0.3.3
