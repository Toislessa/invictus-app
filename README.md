# invictus-app

Pelo meu entendimento, as principais necessidades do meu projeto dizem respeito à sua celeridade e eficiência. Ele funciona e não há erros. Todavia, considerando o tamanho do projeto, considerando que será um programa em produção, que será acessado por muito usuários na rede. considerando que ele consome muita cpu e memória para realizar as tarefas, principalmente os cálculos, preciso lançar mão de todas as suas sugestões de otimização. Noto que o gargalo principal são os subprocessos. Pois estes estão sendo executados e requisitados o tempo todo, em tempo real. E alguns destes processos, estão se arrastando. Assim, os scripts auxiliares que estão em subprocessos: soma.py, monitor2.py, intervalos13.py, intervalos13_1.py, gráficos4.py e gráficos3.py, todos, estão, de alguma forma, interferindo, negativamente na eficiencia de todo o sistema. Assim, os subprocessos são o primeiro ponto de atenção. Além disto, cada um destes processos, devem receber atenção em separado, pois cada um precisa, uns mais outro menos, de otimizações.

Como são muitos scripts e são scripts grandes e complexos, não daria para compartilhar, copiando e colando aqui. Teria uma forma eficiente de compartilhar todos eles com você, de forma que você poderia consultar à qualquer momento?

2 - Estrutura do Projeto: Falei um pouco da estrutura do projeto no tópico anterior. Mas, basicamente, o meu projeto consiste em um script Dash, que apresenta um Dashboard com 1 gráfico, uma grid (que chamo de catalogador) e duas tabelas. Para cada elemento destes ser atualizado em tempo real, necessita de dados, que são captados pelos scripts auxiliares: soma.py, monitor2.py, intervalos13.py, intervalos13_1.py, gráficos4.py e gráficos3.py. Alguns deles, faz a coleta de dados na plataforma Blaze.com, raspando os dados das jogadas na roleta online. Estes dados, basicamente, são os resultados, à cada rodada, contendo o número sorteado e o horário em que foi sorteado cada número. A partir destes dados, outros scripts fazem a análise dos dados e cálculos. Para tanto, faz a manipulação dos dados com o pandas e grava estes sempre em arquivos csv, que serão lidos pelo Dash.
Este é um resumo. Mas, com este resumo e com a sua análise dos scripts, conseguirá entender, pela sua esperiencia como desenvolvedor de programas python.
3 - Banco de Dados: Vou usar o mySql
4 - Requisitos específicos: A única restrição em termos de bibliotecas versa apenas sobre aquelas que são ineficientes, para o projeto que se quer obter. Ou seja, pense sempre na melhor alternativa para um super robô que irá atuar nas nuvens. À priore, quero muito usar o script Dash, com o Flask, para usar rotas e socket-io. O resto, deixarei pela sua experiência. Todavia, uma grande restrição e fundamental: Pode e deve propor e fazer qualquer alteração, contanto que NUNCA altere NADA da lógica do projeto. Ele precisa ser otimizado, todavia, precisa ser apresentado, EXATAMENTE, da forma que ele é apresentado hoje.
5 - Ambiente de desenvolvimento: Como já sabe, desenvolvo o projeto 100% no windows, com o pycharm
6 - Dados de testes: Posso compartilhar, juntamente com os scripts, os arquivos csv que são gerados pelos scripts auxiliares. Ademais, Posso fazer um print da tela do Dashboard, para você ter uma ideia de como é o frontend. À cada atualização que fizer, vou testar os scripts e passar um feedback para discutir possíveis ajustes.
7 - Restrição de tempo: Sem restrição de tempo.
