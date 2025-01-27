# Criando imagens do HUB

- Instale uma máquina virtual Linux com Ubuntu. Recomenda-se a versão servidor LTS, tal como https://ubuntu.com/download/server/thank-you?version=24.04.1&architecture=amd64&lts=true

- Opções de máquina virtual:
 * Hyper-V (Windows 11 Pro)
 * VirtualBox
 * VMWare
 
- Faça checkout do repositório. Talvez precise adicionar uma chave para acesso ssh.

```
git clone  --recurse-submodules git@github.com:marcelobarrosufu/hub_pi_gen.git
cd hub_pi_gen
```

- configure o git

```
git config --global user.email "marcelo.barros@ufu.br"
git config --global user.name "Marcelo Barros"
```

- Atualize as dependências

```
sudo ./update_deps.sh
```

- Gere a imagem, indicando a versão

```
sudo ./gen_img.sh V2.0.0
```
 
 
