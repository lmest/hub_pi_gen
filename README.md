# Criando imagens do HUB

- Instale uma máquina com distribuição Linux baseda em Ubuntu. Recomenda-se a versão servidor LTS, tal como https://ubuntu.com/download/server/thank-you?version=24.04.1&architecture=amd64&lts=true

- Opções de máquina virtual (Windows somente, MacOS não funciona o pi-gen em VM):
 * Hyper-V (Windows 11 Pro)
 * VirtualBox
 * VMWare
 
- Faça checkout do repositório https://github.com/lmest/hub_pi_gen. Talvez precise adicionar uma chave para acesso ssh. Não se esqueça da opção de recursão.

```
git clone  --recurse-submodules git@github.com:marcelobarrosufu/hub_pi_gen.git
cd hub_pi_gen
```

- configure o git (use suas credenciais abaixo)

```
git config --global user.email "marcelo.barros@ufu.br"
git config --global user.name "Marcelo Barros"
```

- Atualize as dependências

```
sudo ./update_deps.sh
```

- Gere a imagem, indicando o tipo de imagem e a versão (podem ser usados os parâmetros lte ou wifi)

```
sudo ./gen_img.sh lte V2.0.0
sudo ./gen_img.sh wifi V2.0.0
```
 
 
