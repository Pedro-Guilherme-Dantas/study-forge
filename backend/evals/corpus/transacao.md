# Transação (banco de dados)

Uma transação simboliza uma unidade de trabalho executada dentro de um sistema de gerenciamento de banco de dados (ou sistema similar), sobre um banco de dados, e tratada de maneira coerente e confiável, independente de outras transações. Uma transação geralmente representa qualquer alteração em um banco de dados. As transações em um ambiente de banco de dados têm dois propósitos principais:

Fornecer unidades de trabalho confiáveis ​​que permitam a recuperação correta de falhas e manter um banco de dados consistente mesmo em casos de falha do sistema, quando a execução é interrompida (completamente ou parcialmente) e muitas operações em um banco de dados permanecem incompletas, com estado pouco claro.
Fornecer isolamento entre programas que acessam um banco de dados simultaneamente. Se esse isolamento não for fornecido, os resultados dos programas possivelmente serão errôneos.
Em um sistema de gerenciamento de banco de dados, uma transação é uma unidade única de lógica ou de trabalho, às vezes composta de várias operações. Qualquer cálculo lógico feito de um modo consistente em um banco de dados é conhecido como uma transação. Um exemplo é a transferência de uma conta bancária para outra: a transação completa requer a subtração do valor a ser transferido de uma conta e a adição da mesma quantia à outra.
Uma transação de banco de dados, por definição, deve ser atômica, consistente, isolada e durável. Profissionais de banco de dados geralmente se referem a essas propriedades de transações de bancos de dados usando o acrônimo ACID.
As transações fornecem uma proposição "tudo ou nada", afirmando que cada unidade de trabalho executada em um banco de dados deve ser concluída em sua totalidade ou não ter efeito algum. Além disso, o sistema deve isolar cada transação de outras transações, os resultados devem estar em conformidade com as restrições existentes no banco de dados e as transações concluídas com êxito devem ser gravadas no armazenamento durável.


## Conceitos
A integridade de uma transação depende de 4 propriedades, conhecidas como ACID.

Atomicidade
Todas as ações que compõem a unidade de trabalho da transação devem ser concluídas com sucesso, para que seja efetivada. Se durante a transação qualquer ação que constitui unidade de trabalho falhar, a transação inteira deve ser desfeita (rollback). Quando todas as ações são efetuadas com sucesso, a transação pode ser efetivada e persistida em banco (commit).
Consistência
Todas as regras e restrições definidas no banco de dados devem ser obedecidas. Relacionamentos por chaves estrangeiras, checagem de valores para campos restritos ou únicos devem ser obedecidos para que uma transação possa ser completada com sucesso.
Isolamento
Cada transação funciona completamente à parte de outras estações. Todas as operações são parte de uma transação única. O principio é que nenhuma outra transação, operando no mesmo sistema, possa interferir no funcionamento da transação corrente(é um mecanismo de controle). Outras transações não podem visualizar os resultados parciais das operações de uma transação em andamento (ainda em respeito à propriedade da atomicidade).
Durabilidade
Significa que os resultados de uma transação são permanentes e podem ser desfeitos somente por uma transação subsequente. Por exemplo: todos os dados e status relativos a uma transação devem ser armazenados num repositório permanente, não sendo passíveis de falha por uma falha de hardware.


## Sintetizando
Na área de banco de dados, uma transação é uma sequência de operações num sistema de gerência de banco de dados que são tratadas como um bloco único e indivisível (atômico) durante uma recuperação de falhas e também prover isolamento entre acessos concorrentes na mesma massa de dados. Por exemplo, uma transferência de fundos de uma conta-corrente para uma conta de poupança é uma única operação do ponto de vista do cliente; contudo, dentro do sistema de banco de dados, ela consiste em várias operações. Claramente, é essencial que todas essas operações ocorram ou que, no caso de uma falha, nenhuma delas ocorra. Seria inaceitável se a conta-corrente fosse debitada, mas a conta de poupança não fosse creditada.
Essa coleção de operações deve aparecer ao usuário como uma única unidade, indivisível. A transação é indivisível, ela é executada em sua totalidade ou não é executada. Assim, se uma transação começa a ser executada, mas falha por um motivo qualquer, quaisquer mudanças no banco de dados que a transação possa ter feito são desfeitas. Porém, é difícil garantir que esse requisito seja atendido, pois algumas mudanças no banco de dados ainda podem ser armazenadas somente nas variáveis da memória principal da transação, enquanto outras podem ter sido gravadas no banco de dados. Essa propriedade "tudo ou nada" é conhecida como atomicidade.
Além disso, como uma transação é uma unidade única, suas ações não podem ser intercaladas com outras operações do banco de dados que não participam da transação. Até mesmo um único comando SQL envolve muitos acessos separados ao banco de dados, e uma transação pode consistir em vários comandos SQL. Portanto, o sistema de banco de dados precisa tomar ações especiais para garantir que as transações operem corretamente, sem interferência de comandos de bancos de dados executando simultaneamente. Essa é a característica da propriedade chamada isolamento.
Para garantir que o sistema do banco de dados não perca uma transação completada com sucesso a partir de uma falha posterior, as ações de uma transação precisam persistir entre as falhas. Além disso, os resultados de uma transação só podem ser desfeitos por outra transação. Essa propriedade é conhecida como durabilidade.
Devido a essas três propriedades, uma transação precisa preservar a consistência do banco de dados. O modo como isso é feito é responsabilidade do programador que codifica uma transação. Essa propriedade é conhecida como consistência.
O padrão SQL define quatro níveis de isolamento de transação (Read uncommitted, Read committed, Repeatable read, Serializable) em termos de três fenômenos que devem ser evitados entre transações simultâneas. Os fenômenos não desejados são:

dirty read (leitura suja)
A transação lê dados escritos por uma transação simultânea não efetivada (uncommitted). [1]
nonrepeatable read (leitura que não pode ser repetida)
A transação lê novamente dados lidos anteriormente, e descobre que os dados foram alterados por outra transação (que os efetivou após ter sido feita a leitura anterior). [2]
phantom read (leitura fantasma)
A transação executa uma segunda vez uma consulta que retorna um conjunto de linhas que satisfazem uma determinada condição de procura, e descobre que o conjunto de linhas que satisfazem a condição é diferente por causa de uma outra transação efetivada recentemente. [3]
Os quatro níveis de isolamento de transação, e seus comportamentos correspondentes, estão descritos na tabela abaixo:
Níveis de isolamento da transação no SQL


## A partir de onde é Importante
A partir do momento em que a aplicabilidade de transações em Banco de Dados torna possível
que haja uma transação limpa sem complicações eminentes por conta dos cuidados com cada procedimento
que se faz necessário para aplicações que são de suma importância em nosso mundo hoje.


## Façamos uma análise
Suponha que um usuário apresente a seguinte atualização a um banco de dados usado para
processar compensação de cheques bancários.
Debite $100,00 à conta corrente do cliente N
Credite $100,00 à conta corrente do cliente M
Após manipulação pelo processador de consultas, teríamos algo como a seguinte sequência
de ações elementares:

A1 = (LEIA,CONTA_CORRENTE[A].SALDO,X)
A2 = (COMPUTE, W:=X-100)
A3 = (ESCREVA,CONTA_CORRENTE[A].SALDO,W)
A4 = (LEIA,CONTA_CORRENTE[B].SALDO,X)
A2 = (COMPUTE, W:=X+100)
A6 = (ESCREVA,CONTA_CORRENTE[B].SALDO,W)
[[onde A e B são os elementos de CONTA_CORRENTE correspondentes às tuplas de CONTAS
com NUMERO_CONTA = N e NUMERO_CONTA = M, respectivamente.]]
Por alguma razão qualquer (falta de energia, falhas no equipamento ou programas, etc.)., a
atividade do banco de dados é interrompida após a execução da ação elementar A3. Ao
retornar à atividade, teríamos debitado $100,00 à conta de A e ainda não creditado valor
algum à conta de B. Isto colocaria o banco de dados num estado inconsistente, pois $100,00
teriam simplesmente "desaparecido". Seria muito conveniente se pudéssemos assegurar que a
sequência de ações elementares acima tivesse a propriedade de que "ou todas as ações
elementares executam com sucesso ou nenhuma delas é executada". Em outras palavras,
gostaríamos de estender o conceito de atomicidade de modo a envolver agora também
sequências de ações elementares.
A atomicidade de sequência de ações elementares poderia também ser violada por
interferência de outras ações executadas concorrentemente (exemplos serão dados no
Capítulo 8).
A noção de transação é introduzida para forçar o sistema a executar uma sequência de ações
elementares como se fosse uma unidade atômica, sem interferência externa.
A nível lógico, uma transação é definida através de um programa em uma linguagem de alto
nível, contendo comandos da LMD embebidos, e iniciado e terminado pelos comandos
COMEÇO-DE-TRANSAÇÃO e FIM-DE-TRANSAÇÃO. Na sua forma mais simples, uma transação
contém apenas um comando da LMD. Exige-se do usuário que codifique as transações de tal
forma que quando executadas sozinhas:

T1. sempre terminem;
T2. preservem a consistência do banco de dados.
Exige-se do SGBD, por sua vez, que a cada invocação de uma transação T:

S1. a transação T seja executada por completo;
S2. a execução da transação T se dê sem interferência de outras transações que porventura
estejam sendo executadas concorrentemente.
Lembremos que a cada transação T corresponde uma sequência de ações elementares sobre
os objetos físicos. O primeiro requisito, S1, garante então que o efeito líquido, isto é, aquele
que será tornado público após o término da chamada a T, refletirá o fato de que todas ou
nenhuma das ações elementares de T foram executadas. Note que isto não implica que
cada uma das ações de T deva ser ativada apenas uma única vez. Para ver isto, suponha que
existam, no repertório de ações elementares do nó onde T foi executada, as ações elementares
 A1 ,…,  An onde Ai indica a ação elementar de efeito exatamente contrário à Ai
. Em
outras palavras,  Ai devolve o banco de dados ao estado anterior à execução de Ai
.
Retornando ao exemplo anterior sobre compensação bancária, é fácil ver que A1 , como uma
operação de "leitura", não altera o estado do banco. Portanto, seria válido colocar  A1 =
(NULO), isto é, à  A1 não corresponde operação alguma. Idem,  A2 = (NULO).
Continuando,  A3 = (ESCREVA, CONTA_CORRENTE[A].SALDO, X) pois a variável X detém o
conteúdo inicial de CONTA_CORRENTE[A].SALDO até o término da transação. Note que isto
restaura o valor do objeto CONTA_CORRENTE[A] ao valor que apresentava antes da execução
de A3. Podemos definir  A4,  A5 e  A6 analogamente.
Dentro deste espírito, se E = (A1, A2, A3, A4) for a sequência de ações elementares gerada por
uma execução sequencial de T, então cada uma das sequências de ações elementares abaixo,
quando ativadas pelo sistema, satisfazem ao requisito contido no item (1) acima.
A1 , A2 , A3 , A4
A1 , A2 , A2 , A2 , A3 , A4 , A4 , A4
A1 , A1 , A1 , A1 , A1 , A2 , A3 ,  A3 , A2 , A1 , A1 , A2 , A3 , A4
Na realidade, embora as ações elementares  Ai pareçam um tanto obtusas no momento,
desempenharão um papel crucial nas ideias a serem desenvolvidas mais adiante. O leitor
atento já deve ter percebido isto. Voltando ao exemplo da compensação bancária, caso o
sistema falhe após a execução das ações elementares A1 , A2 e A3 , e supondo que os objetos
envolvidos residam em memória secundária, ao retornar à atividade o banco de dados estaria
em um estado refletindo uma execução parcial de T. Neste ponto, após executada as ações
U = ( A3 , A2 , A1 ) o banco de dados recairia novamente em um estado que não reflete
nenhuma ação de T, podendo retomar suas atividades normais.
O segundo requisito, S2, não exclui a possibilidade de intercalar ações elementares de
transações diferentes sobre o mesmo banco de dados local, ou de executar paralelamente
ações elementares da mesma transação ou de transações diferentes sobre bancos de dados
locais distintos. No entanto, o requisito S2 exige que algum controle seja exercido para que o
nível de concorrência permitido não destrua a ideia de atomicidade da execução das
transações.


## Executando Transações: Início, Migração E Término
Recordemos inicialmente a arquitetura para SGBDDs introduzida na Seção 1.1.3. Em um
primeiro nível, esta arquitetura divide o SGBDD em uma coleção de SGBDs locais
interligados pelo SGBD global. Cada nó da rede possui uma cópia do SGBD global. Este, por
sua vez, é dividido em três grandes componentes:

1. diretório de dados global (DDG): contém descrições dos objetos lógicos e físicos e
dos mapeamentos entre estes;

2. gerente de transações (GT): interpreta e controla o processamento de consultas e
transações submetidas ao sistema;

3. gerente de dados (GD): interface com o SGBD local, fazendo as traduções necessárias
no caso de sistemas heterogêneos.
O propósito desta seção será apresentar em mais detalhe como um GT processa transações.

Em uma primeira fase:
 coordenador: envia, a todos os nós participantes, mensagens na forma PREPARE-SE.
 cada nó participante

1. ao receber uma mensagem de PREPARE-SE vinda do coordenador, tenta
registrar em memória estável, isto é, de forma que sobreviva à eventuais falhas
do sistema, os efeitos locais da transação

2. a seguir, envia ao coordenador mensagens na forma PREPARADO caso tenha
conseguido o registro em memória estável, ou na forma IMPOSSIBILITADO
em caso contrário

Numa segunda fase:
 coordenador

1. envia a todos os nós participantes a mensagem CONFIRME, caso deseje
confirmar a transação e todos os nós participantes tenham remetido a
mensagem PREPARADO na primeira fase;

2. em qualquer outro caso, o coordenador envia a mensagem CANCELE a todos
os nós participantes
 cada nó participante: ao receber o veredito do coordenador, procede de acordo com
este.


## Ver também
Processamento de transação


## Referências
