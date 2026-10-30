# Número primo

Um número primo é um número natural maior que 1 que não pode ser formado pela multiplicação de outros dois naturais menores. Um número natural maior que 1 que não é primo é chamado de número composto. Por exemplo, 5 é primo porque as únicas maneiras de escrevê-lo como um produto, 1 × 5 ou 5 × 1, envolvem o próprio 5. No entanto, 4 é composto porque é um produto (2 × 2) no qual ambos os números são menores que 4. Os primos são centrais na teoria dos números devido ao teorema fundamental da aritmética: todo número natural maior que 1 ou é um primo, ou pode ser fatorado como um produto de primos de maneira única, salvo pela ordem dos fatores.
A propriedade de ser primo é chamada primalidade. Um método simples, mas lento, de verificar a primalidade de um número dado n, chamado de divisão por tentativa, testa se n é um múltiplo de qualquer inteiro entre 2 e 
  
    
      
        
          
            n
          
        
      
    
    {\displaystyle {\sqrt {n}}}
  
. Algoritmos mais rápidos incluem o teste de primalidade de Miller–Rabin, que é rápido, mas tem uma pequena chance de erro, e o teste de primalidade AKS, que sempre produz a resposta correta em tempo polinomial, mas é muito lento para ser prático. Métodos particularmente rápidos estão disponíveis para números de formas especiais, como números de Mersenne. Em outubro de 2024, o maior número primo conhecido é um número primo de Mersenne com 41 024 320 algarismos.
Há infinitos números primos, como demonstrado por Euclides por volta de 300 a.C. Não existe uma fórmula simples conhecida que distinga números primos de números compostos. No entanto, a distribuição de números primos nos números naturais em geral pode ser modelada estatisticamente. O primeiro resultado nessa direção é o teorema dos números primos, provado no final do século XIX, que afirma que a probabilidade aproximada de um número grande escolhido aleatoriamente ser primo é inversamente proporcional ao número de seus dígitos, ou seja, ao seu logaritmo.
Várias questões históricas relacionadas a números primos continuam sem solução. Estas incluem a conjectura de Goldbach, que afirma que todo número inteiro par maior que 2 pode ser expresso como a soma de dois números primos, e a conjectura dos números primos gêmeos, que diz que existem infinitos pares de números primos cuja diferença é igual a dois. Tais questões estimularam o desenvolvimento de várias áreas da teoria dos números, concentrando-se em aspectos analíticos ou algébricos dos números. Números primos são utilizados em diversos procedimentos na tecnologia da informação, como na criptografia de chave pública, que depende da dificuldade de decompor números grandes em seus fatores primos. Na álgebra abstrata, objetos que se comportam de maneira generalizada como números primos incluem elementos primos e ideais primos.


## Definição e exemplos
Um número natural (1, 2, 3, 4, 5, 6 etc.) é chamado de número primo se é maior que 1 e não pode ser escrito como o produto de dois números naturais menores. Os números maiores que 1 que não são primos são chamados de números compostos. Noutras palavras, n é primo se n elementos não podem ser divididos em grupos menores, porém maior que apenas um, de mesma quantidade, ou não é possível organizar n pontos em uma grade retangular que possui mais de um ponto de altura ou largura. Por exemplo, entre os números de 1 a 6, os números 2, 3 e 5 são primos, visto que não há nenhum outro número que os divida igualmente (sem deixar resto). 1 não é primo, visto que é especificadamente excluído da definição. 4 = 2 × 2 e 6 = 2 × 3 são ambos compostos.

Os divisores de um número natural n são os números naturais que dividem igualmente n. Todo número natural tem tanto 1 quanto ele mesmo como divisores. Se ele possuir qualquer outro divisor além desses dois, então não será primo. Isso leva a uma definição equivalente de número primo: são os números que possuem exatamente dois divisores positivos. Esses dois números são justamente 1 e ele mesmo. Como 1 possui apenas um único divisor, ele mesmo, não é primo por definição. Ainda, outra maneira de expressar a mesma coisa, é que um número n é primo se é maior que um e nenhum dos números 2, 3, ... , n − 1 divide igualmente n.
Os primeiros 25 números primos (todos os primos menores que 100) são:

2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97 (sequência A000040 na OEIS)
Nenhum número par n maior que 2 é primo, visto que tal número pode ser expresso como o produto 2 × n/2. Portanto, Todo número primo além do 2 é um número impar. Similarmente, quando escrito no sistema decimal usual, todos os números primos maiores que 5 terminam em 1, 3, 7 ou 9. Os números que terminam com os outros dígitos são sempre compostos: um número decimal terminado nos dígitos 0, 2, 4, 6 ou 8 são pares, e os números decimais que terminam em 0 ou 5 são divisíveis por 5.
O conjunto de todos os primos é às vezes denotado pela letra P (uma letra P maiúscula em negrito) ou por 
  
    
      
        
          P
        
      
    
    {\displaystyle \mathbb {P} }
  
 (uma letra P maiúscula em blackboard bold)


## História
A origem do conceito número primo é incerta, todavia, há um indício de consciência desses números demonstrado pelo osso de Ishango, um achado ósseo datado do Paleolítico Superior, no qual aparecem sinais representando os números primos entre 10 e 20, mas isso pode ser apenas uma coincidência. Outro indício pode ser observado na mesopotâmia no segundo milênio a.C., onde há tábuas contendo soluções para alguns problemas aritméticos relativos que, para serem solucionados, requerem um conhecimento de fatoração em números primos. No mesmo milênio, datado de aproximadamente 1550 a.C., o Papiro de Rhind tem expansões de frações egípcias de diferentes formas para números primos e compostos. As expansões de números que compartilham o menor dos seus fatores são semelhantes, sugerindo que os egípcios estavam pelo menos cientes da diferença entre números primos e compostos.
No mesmo período, há indícios de que os chineses também possuíam um entendimento desses números. Aproximadamente no ano 1000 a.C., associavam características femininas aos números pares e características masculinas aos ímpares, considerando ímpares não primos, como 15, "efeminados". Eles utilizavam um método físico para a identificação de números primos: ao tentar dispor uma certa quantidade de grãos em retângulos, percebiam que números primos, como 17, somente permitiam uma disposição em linha única, enquanto números compostos, como 15, podiam ser arranjados em retângulos menores.
Entretanto, o primeiro registro sobrevivente do estudo de números primos vem dos matemáticos da Grécia Antiga, que os chamaram de prōtos arithmòs (πρῶτος ἀριθμὸς). Os Elementos de Euclides prova a infinidade dos números primos e o teorema fundamental da aritmética, e mostra como construir um número perfeito a partir de um primo de Mersenne. Outra invenção grega, o crivo de Eratóstenes, ainda é utilizado para construir listas de primos. Os séculos seguintes foram marcados por um certo desinteresse pelo estudo dos números primos, sem haver resultados relevantes neste tópico.
Por volta de 1000 d.C., o matemático islâmico Alhazém enunciou o teorema de Wilson, caracterizando os números primos como os números n dividem igualmente (n − 1)! + 1. Ele também conjecturou que todo número perfeito par vêm da construção de Euclides usando primos de Mersenne, mas não conseguiu prová-la. Outro matemático islâmico, Ibne Albana de Marraquexe, observou que o crivo de Eratóstenes pode ser agilizado considerando apenas os divisores primos até a raiz quadrada da cota superior. Fibonacci levou as inovações dos matemáticos islâmicos à Europa. No seu livro Liber Abaci (1202), foi o primeiro a descrever a divisão por tentativa para realizar o teste de primalidade, novamente utilizando divisores somente até à raiz quadrada do número a ser realizado o teste.
Em 1640, Pierre de Fermat afirmou (sem provar) o pequeno teorema de Fermat (que posteriormente foi provado por Leibniz e Euler) e o teorema de Fermat sobre somas de dois quadrados (provado por Euler). Fermat também investigou a primalidade dos números de Fermat 22n + 1, e Marin Mersenne estudou os primos de Mersenne, primos da forma 2p − 1 com p primo. Christian Goldbach formulou a conjectura de Goldbach, que todo número par é a soma de primos, numa carta de 1742 para Euler. Euler provou a conjectura de Alhazém (agora chamado de teorema de Euclides–Euler [en]) que dizia que todo número perfeito par pode ser construído a partir de primos de Mersenne. Ele introduziu métodos da análise matemática a esta área nas suas provas da infinitude dos números primos e a divergência da série dos inversos dos primos 
  
    
      
        
          
            
              1
              2
            
          
        
        +
        
          
            
              1
              3
            
          
        
        +
        
          
            
              1
              5
            
          
        
        +
        
          
            
              1
              7
            
          
        
        +
        
          
            
              1
              11
            
          
        
        +
        ⋯
      
    
    {\displaystyle {\tfrac {1}{2}}+{\tfrac {1}{3}}+{\tfrac {1}{5}}+{\tfrac {1}{7}}+{\tfrac {1}{11}}+\cdots }
  
. No início do século XIX, Legendre e Gauss conjecturaram que conforme x tende a infinito, o número de primos menores que x é assintótico a x/log x, onde log x é o logaritmo natural de x. Uma pequena consequência dessa alta densidade de primos era o postulado de Bertrand, que para todo n > 1, existe pelo menos um primo entre n e 2n, provado em 1852 por Pafnuty Chebyshev. As ideias de Bernhard Riemann no seu artigo de 1859 sobre a função zeta esboçaram uma prova da conjectura de Legendre e Gauss. Apesar de a hipótese de Riemann, intimamente relacionada, ainda não tenha sido comprovada, o esboço de Riemann foi concluído em 1896 por Hadamard e de la Vallée Poussin, e agora o resultado é conhecido como o teorema dos números primos. Outro importante resultado do século XIX foi o teorema de Dirichlet sobre progressões aritméticas, que afirma que certas progressões aritméticas possuem infinitos números primos.
Diversos matemáticos trabalharam em testes de primalidade para números demasiados grandes, os quais a divisão por tentativa torna-se inviável. Alguns métodos são restritos a algum tipo específico de número, como o teste de Pépin para números de Fermat (1877), o teorema de Proth (c. 1878), o teste de primalidade de Lucas–Lehmer (originalmente desenvolvido em 1878) e o teste de primalidade de Lucas generalizado. Desde 1951, todos os maiores primos conhecidos foram encontrados utilizando esses testes em computadores. A pesquisa por números primos cada vez maiores gerou interesses fora do círculo da matemática pelo Great Internet Mersenne Prime Search e outros projetos de processamento distribuído. A ideia de que os números primos tinham poucas aplicações fora da matemática pura foi desfeita na década de 1970, quando a criptografia de chave pública e o sistema de criptografia RSA foram inventados, usando números primos como base.
O aumento da importância prática dos testes de primalidade e da fatoração computadorizados levou ao desenvolvimento de métodos aprimorados capazes de lidar com um grande número de formas irrestritas. A teoria matemática também avançou com o teorema de Green–Tao (2004), que afirma a existência de progressões aritméticas comprimento arbitrário de números primos, e a prova de 2013 de Yitang Zhang de que existem intervalos entre primos de tamanho limitado.


### Primalidade do um
A maioria dos antigos gregos nem consideravam 1 ser um número, então eles nem consideravam a sua primalidade. Alguns estudiosos da tradição grega e da romana, incluindo Nicômaco, Jâmblico, Boécio e Cassiodoro, consideravam os números primos como uma subdivisão dos números ímpares, então também não consideravam o 2 ser primo. No entanto, Euclides e a maioria dos outros matemáticos gregos consideravam 2 um número primo. Os matemáticos islâmicos medievais seguiram em grande parte os gregos ao considerar que 1 não era um número. Na Idade Média e Renascença, matemáticos começaram a tratar o 1 como um número, e por volta do século XVII alguns deles incluia-o como o primeiro número primo. Em meados do século XVIII, Christian Goldbach listou 1 sendo primo em sua correspondência com Leonhard Euler; porém, o próprio Euler não considerava 1 como primo. Ainda no século XIX, diversos matemáticos ainda consideravam 1 ser primo, e listas de números primos que incluíam 1 continuaram a ser publicadas até 1956. Entretanto, por volta dessa época, no início do século XX, os matemáticos começaram a concordar que 1 não deveria ser classificado como um número primo.
Se a definição de número primo fosse alterada para incluir o 1, diversas afirmações envolvendo números precisariam ser reformuladas de uma forma mais complicada. Por exemplo, o teorema fundamental da aritmética teria que ser reescrita para em termos de fatores maiores que 1, pois todo número poderia ter múltiplas decomposições com diferentes quantidades de cópias de 1. Similarmente, o crivo de Eratóstenes não funcionaria adequadamente se 1 fosse tratado como primo, pois eliminaria todos os múltiplos de 1 (isto é, todos os outros números) e resultaria em apenas um único número 1. Algumas outras propriedades mais técnicas dos primos também não iria funcionar para o número 1: por exemplo, as fórmulas para a função totiente de Euler ou para a função soma dos divisores são diferentes para números primos e para 1. No início do século XX, matemáticos começaram a concordar que 1 não deveria ser listado como primo, mas sim uma categoria própria especial chamada "unidade".


## Propriedades elementares
### Unicidade da decomposição
Escrever um número como um produto de números primos é chamado de decomposição em fatores primos de um número. Por exemplo:

  
    
      
        
          
            
              
                50
              
              
                
                =
                2
                ×
                5
                ×
                5
              
            
            
              
              
                
                =
                2
                ×
                
                  5
                  
                    2
                  
                
                .
              
            
          
        
      
    
    {\displaystyle {\begin{aligned}50&=2\times 5\times 5\\&=2\times 5^{2}.\end{aligned}}}
  

Os termos do produto são chamados de fatores primos. O mesmo fator primo pode aparecer mais de uma vez; nesse exemplo, há duas cópias do fator primo 5. Quando um primo aparece mais de uma vez, pode ser utilizado a exponenciação para agrupar as múltiplas cópias do mesmo número: para esse exemplo, na segunda maneira de escrita do produto acima, 52 indica o quadrado de 5.
A principal importância dos números primos para a teoria dos números e a matemática em geral deriva do teorema fundamental da aritmética. Este teorema afirma que todo número inteiro maior que 1 pode ser escrito como o produto de um ou mais primos. Mais fortemente, este produto é único no sentido que quaisquer duas decomposições de um mesmo número terão os mesmos números de cópias dos mesmos primos, apesar de que a ordem dos fatores pode alterar. Então, embora existam diferentes formas de encontrar a decomposição usando um algoritmo de fatoração de inteiros, todos eles deverão produzir o mesmo resultado. Os números primos podem ser considerados os "blocos fundamentais de construção" dos números naturais.
Algumas provas da unicidade da decomposição se baseiam no lema de Euclides: Se p é um número primo e p divide o produto ab dos inteiros a e b, então p divide a ou p divide b (ou ambos). Por outro lado, se um número p tem a propriedade de ao dividir um produto, ele sempre divide pelo menos um dos fatores do produto, então p deve ser primo.


### Infinitude
Existem infinitos números primos. Outra maneira de dizer isto é que a sequência de números primos

2, 3, 5, 7, 11, 13, ...
nunca acaba. Esta afirmação é referida como o teorema de Euclides, em homenagem ao antigo matemático grego Euclides, já que a primeira prova conhecida para esta afirmação é atribuída a ele. Diversas outras provas da infinitude dos números primos são conhecidas, incluindo uma prova analítica de Euler, uma prova de Goldbach baseada nos números de Fermat, a prova de Furstenberg usando topologia geral e a elegante prova de Kummer.
O teorema de Euclides mostra que toda lista finita de primos é incompleta. A ideia-chave é multiplicar todos os primos da dada lista e somar 1. A lista consiste de primos p1, p2, ..., pn, o que dá o número

  
    
      
        N
        =
        
          p
          
            1
          
        
        ⋅
        
          p
          
            2
          
        
        ⋯
        
          p
          
            n
          
        
        +
        1.
      
    
    {\displaystyle N=p_{1}\cdot p_{2}\cdots p_{n}+1.}
  

Pelo teorema fundamental da aritmética, existe algum primo p pertencente à lista que divide N. Entretanto, todos os elementos da lista dividem o produto p1 · p2 ⋯ pn e, portanto, se p divide N, então p divide 1, o que é um absurdo. Como não há uma lista finita de todos os primos, então existem infinitos números primos.
Os números formados por adicionar um ao produto de um número primo por todos os primos menores que ele são chamados de números de Euclides. Os cinco primeiros deles são primos, mas o sexto,

  
    
      
        1
        +
        
          
            (
          
        
        2
        ⋅
        3
        ⋅
        5
        ⋅
        7
        ⋅
        11
        ⋅
        13
        
          
            )
          
        
        =
        30031
        =
        59
        ⋅
        509
        ,
      
    
    {\displaystyle 1+{\big (}2\cdot 3\cdot 5\cdot 7\cdot 11\cdot 13{\big )}=30031=59\cdot 509,}
  

é um número composto.


### Fórmulas para números primos
Nenhuma fórmula eficiente para encontrar números primos é conhecida. Por exemplo, não há nenhum polinômio não constante, mesmo em várias variáveis, que resulte em apenas valores primos. Porém, existem diversas expressões que codificam todos os primos, ou apenas primos. Uma possível fórmula é baseado no teorema de Wilson e gera o número 2 diversas vezes e todos os outros números primos exatamente uma vez.
Outra fórmula, publicada por Willans em 1964, é

  
    
      
        
          p
          
            n
          
        
        =
        1
        +
        
          ∑
          
            i
            =
            1
          
          
            
              2
              
                n
              
            
          
        
        
          ⌊
          
            
              (
              
                
                  n
                  
                    
                      ∑
                      
                        j
                        =
                        1
                      
                      
                        i
                      
                    
                    
                      ⌊
                      
                        
                          (
                          
                            cos
                            ⁡
                            
                              
                                
                                  (
                                  j
                                  −
                                  1
                                  )
                                  !
                                  +
                                  1
                                
                                j
                              
                            
                            π
                          
                          )
                        
                        
                          2
                        
                      
                      ⌋
                    
                  
                
              
              )
            
            
              1
              
                /
              
              n
            
          
          ⌋
        
        ,
      
    
    {\displaystyle p_{n}=1+\sum _{i=1}^{2^{n}}\left\lfloor \left({\frac {n}{\sum _{j=1}^{i}\left\lfloor \left(\cos {\frac {(j-1)!+1}{j}}\pi \right)^{2}\right\rfloor }}\right)^{1/n}\right\rfloor ,}
  

que computa o n-ésimo número primo pn. Essa fórmula também é ineficaz, pois, além de conter o termo 
  
    
      
        (
        j
        −
        1
        )
        !
      
    
    {\displaystyle (j-1)!}
  
, ela calcula o valor pn somando pn vezes o número 1; por exemplo,

  
    
      
        
          p
          
            5
          
        
        =
        1
        +
        1
        +
        1
        +
        1
        +
        1
        +
        1
        +
        1
        +
        1
        +
        1
        +
        1
        +
        1
        +
        0
        +
        0
        +
        ⋯
        +
        0
        =
        11.
      
    
    {\displaystyle p_{5}=1+1+1+1+1+1+1+1+1+1+1+0+0+\dots +0=11.}
  

Os artigos What is an Answer? de Herbert Wilf (1982) e Formulas for Primes de Underwood Dudley (1983) discutem mais sobre a inutilidade de tais fórmulas.
Há também um conjunto de equações diofantinas em nove variáveis e um parâmetro com a seguinte propriedade: o parâmetro é primo se, e somente se, o sistema de equações resultante tiver uma solução sobre os números naturais. Isso pode ser usado para obter uma única fórmula com a propriedade de que todos os seus valores positivos são primos.
Outros exemplos de fórmulas geradoras de números primos vêm do teorema de Mills e de um teorema de Wright. Eles afirmam que existem as constantes reais A > 1 e μ tais que

  
    
      
        
          ⌊
          
            A
            
              
                3
                
                  n
                
              
            
          
          ⌋
        
        
           e 
        
        
          ⌊
          
            2
            
              
                ⋯
                
                  
                    2
                    
                      
                        2
                        
                          μ
                        
                      
                    
                  
                
              
            
          
          ⌋
        
      
    
    {\displaystyle \left\lfloor A^{3^{n}}\right\rfloor {\text{ e }}\left\lfloor 2^{\cdots ^{2^{2^{\mu }}}}\right\rfloor }
  

são primos para qualquer número natural n na primeira fórmula, e qualquer número de exponentes na segunda fórmula. Aqui 
  
    
      
        ⌊
        

        
        ⋅
        

        
        ⌋
      
    
    {\displaystyle \lfloor {}\cdot {}\rfloor }
  
 representa a função piso, ou seja, o maior número inteiro que seja menor ou igual ao número em questão. Entretanto, essas fórmulas não são úteis para generalizar primos, visto que primeiramente deve ser gerado os números primos para poder computar os valores de A ou μ.


### Questões em aberto
Diversas conjecturas sobre números primos foram propostas. Muitas dessas conjecturas, geralmente com uma formulação elementar, têm resistido à prova durante décadas: todas os quatro problemas de Landau de 1912 continuam em aberto. Um desses problemas é a conjectura de Goldbach, que afirma que todo número inteiro n maior que 2 pode ser escrito como a soma de dois primos Em 2014, essa conjectura foi verificada para todos os números até n = 4×1018. Afirmações mais fracas que essa já foram provadas, como, por exemplo, o teorema de Vinogradov, que diz que todo ímpar suficientemente grande pode ser escrito como a soma de três primos. O teorema de Chen diz que todo par suficientemente grande pode ser escrito como a soma de um primo e um semiprimo (produto de dois primos). Também, qualquer par maior que 10 pode ser escrito como a soma de seis primos. O ramo da teoria dos números que estuda tais questões se chama teoria aditiva dos números.
Outro tipo de problema está relacionado aos intervalos entre primos, isto é, a diferença entre primos consecutivos. A existência de intervalos entre primos de tamanho arbitrário pode ser observada na sequência n! + 2, n! + 3, ..., n! + n, que consiste de n − 1 números compostos, para qualquer número natural n. Entretanto, intervalos maiores podem ocorrer muito antes do que este argumento apresenta. Por exemplo, o primeiro intervalo de 8 unidades ocorre entre os primos 89 e 97, muito menor do que 8! = 40320. É conjecturado que existem infinitos números primos gêmeos, que são pares de primos cuja diferença é 2; esta é a conjectura dos primos gêmeos. A conjectura de Polignac é mais generalizada, afirmando que para cada inteiro positivo k, existem infinitos pares de primos consecutivos cujas diferenças são iguais a 2k. A conjectura de Andrica, a conjectura de Brocard, a conjectura de Legendre e a conjectura de Oppermann sugerem que o maior intervalo entre primos de 1 a n deve ser de aproximadamente 
  
    
      
        
          
            n
          
        
      
    
    {\displaystyle {\sqrt {n}}}
  
, um resultado conhecido por seguir a hipótese de Riemann, enquanto a conjectura de Cramér, muito mais forte, define o maior intervalo entre primos com o tamanho de 
  
    
      
        O
        (
        (
        log
        ⁡
        n
        
          )
          
            2
          
        
        )
      
    
    {\displaystyle O((\log n)^{2})}
  
. Intervalos entre primos podem ser generalizados a n-uplas de números primos, que são definidas para diferenças entre mais de dois números primos. A infinitude e densidade são assuntos da primeira conjectura de Hardy–Littlewood, que podem ser motivados pela heurística de que os números primos se comportam de forma semelhante a uma sequência aleatória de números com densidade dada pelo teorema dos números primos.


### Teoria dos números
Sabe-se que, à medida que avançamos na sequência dos números inteiros, os primos tornam-se cada vez mais raros. Isto levanta duas questões: O conjunto dos números primos seria finito ou infinito? Dado um número natural 
  
    
      
        n
        ,
      
    
    {\displaystyle n,}
  
 qual é a proporção de números primos entre os números menores que 
  
    
      
        n
      
    
    {\displaystyle n}
  
?

A resposta à primeira questão é que o conjunto dos primos é infinito, um resultado conhecido na parte central dos Elementos de Euclides, que lida com as propriedades dos números. Na proposição 20, Euclides explica uma verdade simples porém fundamental sobre os números primos: existe um número infinito deles. Pode-se demonstrar, em notação moderna, da seguinte forma:
Supondo que o número de primos seja finito e sejam 
  
    
      
        
          p
          
            1
          
        
        ,
         
        
          p
          
            2
          
        
        ,
         
        
          p
          
            3
          
        
        ,
         
        .
        .
        .
        ,
         
        
          p
          
            n
          
        
      
    
    {\displaystyle p_{1},\ p_{2},\ p_{3},\ ...,\ p_{n}}
  
 os primos. Seja 
  
    
      
        P
      
    
    {\displaystyle P}
  
 o número tal que

  
    
      
        P
      
    
    {\displaystyle P}
  
 = 
  
    
      
        
          ∏
          
            i
            =
            1
          
          
            n
          
        
        
          p
          
            i
          
        
        +
        1
        ,
      
    
    {\displaystyle \prod _{i=1}^{n}p_{i}+1,}
  
 onde 
  
    
      
        ∏
      
    
    {\displaystyle \prod }
  
 denota o produtório.

Se 
  
    
      
        P
      
    
    {\displaystyle P}
  
 é um número primo, é necessariamente diferente dos primos 
  
    
      
        
          p
          
            1
          
        
        ,
         
        
          p
          
            2
          
        
        ,
         
        
          p
          
            3
          
        
        ,
         
        .
        .
        .
        ,
         
        
          p
          
            n
          
        
        ,
      
    
    {\displaystyle p_{1},\ p_{2},\ p_{3},\ ...,\ p_{n},}
  
 pois sua divisão por qualquer um deles tem um resto de 1.
Por outro lado, se 
  
    
      
        P
      
    
    {\displaystyle P}
  
 é composto, existe um número primo 
  
    
      
        q
      
    
    {\displaystyle q}
  
 tal que 
  
    
      
        q
      
    
    {\displaystyle q}
  
 é divisor de 
  
    
      
        P
        .
      
    
    {\displaystyle P.}
  

Mas obviamente 
  
    
      
        q
        ≠
         
        
          p
          
            1
          
        
        ,
        
        
          p
          
            2
          
        
        ,
        
        .
        .
        .
        ,
        
        
          p
          
            n
          
        
        .
      
    
    {\displaystyle q\neq \ p_{1},\;p_{2},\;...,\;p_{n}.}
  
 Logo existe um novo número primo.
Há um novo número primo, seja 
  
    
      
        P
      
    
    {\displaystyle P}
  
 primo ou composto; este processo pode ser repetido indefinidamente, logo há um número infinito de números primos.
Uma outra prova envolve considerar um número inteiro 
  
    
      
        n
        >
        1.
      
    
    {\displaystyle n>1.}
  
 Temos 
  
    
      
        n
        +
        1
      
    
    {\displaystyle n+1}
  
 que, necessariamente, é coprimo de 
  
    
      
        n
      
    
    {\displaystyle n}
  
 (números coprimos são os que não têm nenhum fator comum maior do que 
  
    
      
        1
      
    
    {\displaystyle 1}
  
). Provamos isto imaginando que a divisão do menor pelo maior tem resultado 
  
    
      
        0
      
    
    {\displaystyle 0}
  
 e resto 
  
    
      
        n
      
    
    {\displaystyle n}
  
 e do maior pelo menor tem resultado 
  
    
      
        1
      
    
    {\displaystyle 1}
  
 e resto 
  
    
      
        1.
      
    
    {\displaystyle 1.}
  
 Assim, 
  
    
      
        n
        (
        n
        +
        1
        )
      
    
    {\displaystyle n(n+1)}
  
 tem, necessariamente, ao menos dois factores primos.
Tomemos o sucessor deste, que representamos como 
  
    
      
        n
        (
        n
        +
        1
        )
        +
        1.
      
    
    {\displaystyle n(n+1)+1.}
  
 Pelo mesmo raciocínio, ele é coprimo a 
  
    
      
        n
        (
        n
        +
        1
        )
        .
      
    
    {\displaystyle n(n+1).}
  
 Ao multiplicar os dois números, temos 
  
    
      
        [
        n
        (
        n
        +
        1
        )
        ]
        ∗
        [
        n
        (
        n
        +
        1
        )
        +
        1
        ]
        .
      
    
    {\displaystyle [n(n+1)]*[n(n+1)+1].}
  
 Como um de seus fatores tem pelo menos dois factores primos diferentes e é coprimo ao outro, o resultado da multiplicação tem pelo menos três factores primos distintos. Este raciocínio também pode ser infinitamente estendido.
A resposta para a segunda pergunta acima é que essa proporção é aproximadamente 
  
    
      
        
          
            n
            
              ln
              ⁡
              (
              n
              )
            
          
        
        ,
      
    
    {\displaystyle {\frac {n}{\ln(n)}},}
  
 onde 
  
    
      
        ln
      
    
    {\displaystyle \ln }
  
 é o logaritmo natural.
Para qualquer número inteiro 
  
    
      
        k
        ,
      
    
    {\displaystyle k,}
  
 existem 
  
    
      
        k
      
    
    {\displaystyle k}
  
 números inteiros consecutivos todos compostos.
O produto de qualquer sequência de 
  
    
      
        k
      
    
    {\displaystyle k}
  
 números inteiros consecutivos é divisível por 
  
    
      
        k
        !
      
    
    {\displaystyle k!}
  

Se 
  
    
      
        k
      
    
    {\displaystyle k}
  
 não é primo, então 
  
    
      
        k
      
    
    {\displaystyle k}
  
 possui, necessariamente, um fator primo menor do que ou igual a 
  
    
      
        
          
            k
          
        
        .
      
    
    {\displaystyle {\sqrt {k}}.}
  

Todo inteiro maior que 1 pode ser representado de maneira única como o produto de fatores primos


## Grupos e sequências de números primos
Pierre de Fermat (1601-1665) descobriu que todo número primo da forma 
  
    
      
        4
        n
        +
        1
        ,
      
    
    {\displaystyle 4n+1,}
  
 tal como 
  
    
      
        5
        ,
        13
        ,
        17
        ,
        29
        ,
        37
        ,
        41
        ,
      
    
    {\displaystyle 5,13,17,29,37,41,}
  
 etc., é a soma de dois quadrados. Por exemplo:

  
    
      
        5
        =
        
          1
          
            2
          
        
        +
        
          2
          
            2
          
        
        ,
      
    
    {\displaystyle 5=1^{2}+2^{2},}
  

  
    
      
        13
        =
        
          2
          
            2
          
        
        +
        
          3
          
            2
          
        
        ,
      
    
    {\displaystyle 13=2^{2}+3^{2},}
  

  
    
      
        17
        =
        
          1
          
            2
          
        
        +
        
          4
          
            2
          
        
        ,
      
    
    {\displaystyle 17=1^{2}+4^{2},}
  

  
    
      
        29
        =
        
          2
          
            2
          
        
        +
        
          5
          
            2
          
        
        ,
      
    
    {\displaystyle 29=2^{2}+5^{2},}
  

  
    
      
        37
        =
        
          1
          
            2
          
        
        +
        
          6
          
            2
          
        
        ,
      
    
    {\displaystyle 37=1^{2}+6^{2},}
  

  
    
      
        41
        =
        
          4
          
            2
          
        
        +
        
          5
          
            2
          
        
        .
      
    
    {\displaystyle 41=4^{2}+5^{2}.}
  

Hoje são conhecidos dois grupos de números primos:

  
    
      
        (
        4
        n
        +
        1
        )
      
    
    {\displaystyle (4n+1)}
  
 - que podem sempre ser escritos na forma (
  
    
      
        
          x
          
            2
          
        
        +
        
          y
          
            2
          
        
      
    
    {\displaystyle x^{2}+y^{2}}
  
); e

  
    
      
        (
        4
        n
        −
        1
        )
      
    
    {\displaystyle (4n-1)}
  
 - nunca podem ser escritos na forma (
  
    
      
        
          x
          
            2
          
        
        +
        
          y
          
            2
          
        
      
    
    {\displaystyle x^{2}+y^{2}}
  
).
Tratando-se de números primos é perigoso fazer uma generalização apenas com base numa observação, não solidamente comprovada matematicamente. Vejamos o exemplo:

  
    
      
        31
      
    
    {\displaystyle 31}
  
, 
  
    
      
        331
        ,
        3.331
        ,
        33.331
        ,
        333.331
        ,
        3.333.331
      
    
    {\displaystyle 331,3.331,33.331,333.331,3.333.331}
  
 e 
  
    
      
        33.333.331
      
    
    {\displaystyle 33.333.331}
  
 são primos
mas 
  
    
      
        333.333.331
      
    
    {\displaystyle 333.333.331}
  
 não é, pois 
  
    
      
        333.333.331
        =
        17
        ×
        19.607.843.
      
    
    {\displaystyle 333.333.331=17\times 19.607.843.}
  

Um olhar mais atento na forma como se distribuem os números primos revela que não há uma regularidade nesta distribuição. Por exemplo existem longos buracos entre os números primos, o número 
  
    
      
        370.261
      
    
    {\displaystyle 370.261}
  
 é seguido de cento e onze números compostos e não existem primos entre os números 
  
    
      
        20.831.323
      
    
    {\displaystyle 20.831.323}
  
 e 
  
    
      
        20.831.533.
      
    
    {\displaystyle 20.831.533.}
  

Algumas fórmulas produzem muitos números primos, por exemplo 
  
    
      
        
          x
          
            2
          
        
        −
        x
        +
        41
      
    
    {\displaystyle x^{2}-x+41}
  
 fornece primos quando 
  
    
      
        x
        =
        0
        ,
         
        1
        ,
         
        2
        ,
         
        .
        .
        .
        ,
         
        40.
      
    
    {\displaystyle x=0,\ 1,\ 2,\ ...,\ 40.}
  
  Veja que para x = 41, a fórmula resulta em 
  
    
      
        
          41
          
            2
          
        
      
    
    {\displaystyle 41^{2}}
  
 que não é primo.
Não existe uma fórmula que forneça primos para todos os valores primos de 
  
    
      
        x
        ,
      
    
    {\displaystyle x,}
  
 de fato em 1752 Goldbach provou que não há uma expressão polinomial em 
  
    
      
        x
      
    
    {\displaystyle x}
  
 com coeficientes inteiros que possa fornecer primos para todos os valores de 
  
    
      
        x
        .
      
    
    {\displaystyle x.}
  

Não se sabe se há uma expressão polinomial 
  
    
      
        a
        
          x
          
            2
          
        
        +
        b
        x
        +
        c
      
    
    {\displaystyle ax^{2}+bx+c}
  
 com 
  
    
      
        a
        ≠
        0
      
    
    {\displaystyle a\neq 0}
  
 que represente infinitos números primos. Dirichlet usou métodos para provar que se 
  
    
      
        a
        ,
      
    
    {\displaystyle a,}
  
 
  
    
      
        2
        b
      
    
    {\displaystyle 2b}
  
 e 
  
    
      
        c
      
    
    {\displaystyle c}
  
 não têm fator primo em comum, a expressão polinomial a duas variáveis

  
    
      
        a
        
          x
          
            2
          
        
        +
        2
        b
        x
        y
        +
        c
        
          y
          
            2
          
        
      
    
    {\displaystyle ax^{2}+2bxy+cy^{2}}
  

representa infinitos primos, quando 
  
    
      
        x
      
    
    {\displaystyle x}
  
 e 
  
    
      
        y
      
    
    {\displaystyle y}
  
 assumem valores positivos inteiros.
Fermat pensou que a fórmula 
  
    
      
        
          2
          
            
              2
              
                n
              
            
          
        
        +
        1
      
    
    {\displaystyle 2^{2^{n}}+1}
  
 forneceria números primos para 
  
    
      
        n
        =
        0
        ,
         
        1
        ,
         
        2
        ,
         
        .
        .
        .
        .
      
    
    {\displaystyle n=0,\ 1,\ 2,\ ....}
  
 Este números são chamados de números de Fermat e são comumente denotados por 
  
    
      
        
          F
          
            n
          
        
        .
      
    
    {\displaystyle F_{n}.}
  
 Os cinco primeiros números são:

  
    
      
        
          F
          
            0
          
        
        =
        3
        ,
        
        
          F
          
            1
          
        
        =
        5
        ,
        
        
          F
          
            2
          
        
        =
        17
        ,
        
        
          F
          
            3
          
        
        =
        257
        
        e
        
        
          F
          
            4
          
        
        =
        65.537
        ,
      
    
    {\displaystyle F_{0}=3,\;F_{1}=5,\;F_{2}=17,\;F_{3}=257\;e\;F_{4}=65.537,}
  

sendo todos primos.


## Aproximações para o n-ésimo primo
Como consequência do teorema do número primo, uma expressão assintótica para o n-ésimo primo 
  
    
      
        
          p
          
            n
          
        
      
    
    {\displaystyle p_{n}}
  
 é:

  
    
      
        
          p
          
            n
          
        
        ∼
        n
        ln
        ⁡
        n
        .
      
    
    {\displaystyle p_{n}\sim n\ln n.}
  

Uma aproximação melhor é:

  
    
      
        
          
            p
            
              n
            
          
          =
          n
          ln
          ⁡
          n
          +
          n
          ln
          ⁡
          ln
          ⁡
          n
          −
          n
          +
          
            
              n
              
                ln
                ⁡
                n
              
            
          
          
            (
            
              ln
              ⁡
              ln
              ⁡
              n
              −
              2
            
            )
          
          −
          
            
              
                n
                ln
                ⁡
                ln
                ⁡
                n
              
              
                2
                (
                ln
                ⁡
                n
                
                  )
                  
                    2
                  
                
              
            
          
          
            (
            
              ln
              ⁡
              ln
              ⁡
              n
              −
              6
            
            )
          
          +
          O
          
            (
            
              
                n
                
                  (
                  ln
                  ⁡
                  n
                  
                    )
                    
                      2
                    
                  
                
              
            
            )
          
          .
        
      
    
    {\displaystyle {p_{n}=n\ln n+n\ln \ln n-n+{\frac {n}{\ln n}}\left(\ln \ln n-2\right)-{\frac {n\ln \ln n}{2(\ln n)^{2}}}\left(\ln \ln n-6\right)+O\left({\frac {n}{(\ln n)^{2}}}\right).}}
  

O teorema de Rosser mostra que 
  
    
      
        
          p
          
            n
          
        
      
    
    {\displaystyle p_{n}}
  
 é maior que 
  
    
      
        n
        ln
        ⁡
        n
        .
      
    
    {\displaystyle n\ln n.}
  
 É possível melhorar esta aproximação com os limites: 
  
    
      
        n
        ln
        ⁡
        n
        +
        n
        (
        ln
        ⁡
        ln
        ⁡
        n
        −
        1
        )
        <
        
          p
          
            n
          
        
        <
        n
        ln
        ⁡
        n
        +
        n
        ln
        ⁡
        ln
        ⁡
        n
      
    
    {\displaystyle n\ln n+n(\ln \ln n-1)<p_{n}<n\ln n+n\ln \ln n}
  
, para 
  
    
      
        n
        ≥
        6.
      
    
    {\displaystyle n\geq 6.}
  


## Métodos computacionais
Por muito tempo, a teoria dos números, em geral, e o estudo dos números primos, em particular, foram vistos como o exemplo canônico da matemática pura, sem aplicações fora da matemática além do uso de dentes de engrenagens com números primos para distribuir o desgaste uniformemente. Em particular, os teóricos dos números, como o matemático britânico G. H. Hardy, orgulhavam-se de fazer um trabalho que não tinha absolutamente nenhum significado militar.
Essa visão da pureza da teoria dos números foi abalada na década de 1970, quando foi anunciado publicamente que os números primos poderiam ser usados como base para a criação de algoritmos de criptografia de chave pública. Esses aplicativos levaram a um estudo significativo de algoritmos para computação com números primos e, em particular, de testes de primalidade, métodos para determinar se um determinado número é primo. A rotina mais básica de teste de primalidade, a divisão por tentativa, é muito lenta para ser útil para números grandes. Um grupo de testes de primalidade modernos é aplicável a números arbitrários, enquanto testes mais eficientes estão disponíveis para números de tipos especiais. A maioria dos testes de primalidade apenas informa se o argumento é primo ou não. As rotinas que também fornecem um fator primo de argumentos compostos (ou todos os seus fatores primos) são chamadas de algoritmos de fatoração. Os números primos também são usados na computação para somas de verificação, tabelas de dispersão e geradores de números pseudoaleatórios.


### Divisão por tentativa
O método mais básico para verificar a primalidade de um determinado número inteiro é chamado de divisão por tentativa. Esse método divide cada número inteiro n de 2 até a raiz quadrada de n. Qualquer número inteiro que se divida igualmente é considerado composto; caso contrário, é primo. Os números inteiros maiores que a raiz quadrada não precisam ser verificados porque, sempre que n = a · b, um dos dois fatores e é menor ou igual à raiz quadrada de n. Outra otimização é verificar apenas os números primos como fatores nesse intervalo. Por exemplo, para verificar se 37 é primo, esse método o divide pelos números primos no intervalo de 2 a 
  
    
      
        
          
            37
          
        
      
    
    {\displaystyle {\sqrt {37}}}
  
, que são 2, 3 e 5. Cada divisão gera um resto diferente de zero e, portanto, 37 é, de fato, primo.
Embora esse método seja simples de descrever, ele não é prático para testar a primalidade de números inteiros grandes, porque o número de testes que ele realiza cresce exponencialmente em função do número de dígitos desses números inteiros. No entanto, a divisão por tentativa ainda é usada, com um limite menor do que a raiz quadrada no tamanho do divisor, para descobrir rapidamente números compostos com fatores pequenos, antes de usar métodos mais complicados nos números que passam por esse filtro.


### Crivos
Antes dos computadores, as tabelas matemáticas que listavam todos os primos ou decomposições em números primos até um determinado limite eram comumente impressas. O método mais antigo conhecido para gerar uma lista de primos é chamado de crivo de Eratóstenes. A animação mostra uma variante otimizada desse método. Outro crivo assintoticamente mais eficiente para o mesmo problema é o crivo de Atkin. Na matemática avançada, a teoria dos crivos aplica métodos semelhantes a outros problemas.


### Teste de primalidade versus prova de primalidade
Alguns dos testes modernos mais rápidos para verificar se um dado número n arbitrário é primo são algoritmos probabilísticos (ou de Monte Carlo), o que significa que eles possuem uma pequena chance aleatória de gerar uma resposta errada. Por exemplo, o teste de primalidade de Solovay–Strassen em um dado número p escolhe um número aleatório a de 2 a p − 2 e usa exponenciação modular para verificar se a(p − 1) ± 1 é divisível por p. Se for divisível, então a resposta é sim, caso contrário, é não. Se p realmente for primo, então a resposta sempre será sim, mas se for composto, então a resposta é sim com a probabilidade de no máximo 1/2 e não com a probabilidade de no mínimo 1/2. Se esse teste é repetido n vezes no mesmo número, a probabilidade de um número composto passar em todos os testes é de no máximo 1/2n. Como essa probabilidade decresce exponencialmente conforme o número de testes aumenta, ele produz uma alta confiança (porém não seja certeza) de que um número que passe por repetidos testes seja primo. Por outro lado, se algum dos testes falhar, então o número é certamente composto. Um número composto que passa por tal teste é chamado de pseudoprimo.
Por outro lado, alguns outros algoritmos garantem que a resposta sempre será correta: os primos sempre serão determinados como primos e os compostos sempre serão determinados como compostos. Isso é verdade para a divisão por tentativa, por exemplo. Os algoritmos que garantem um resultado correto incluem tanto algoritmos determinísticos (não aleatórios), como o teste de primalidade AKS, quanto algoritmos de Las Vegas randomizado, em que as escolhas aleatórias feitas não interferem em sua resposta final, como algumas variações da prova de primalidade por curvas elípticas. Quando o método da curva elíptica conclui que um número é primo, ele gera um certificado de primalidade que pode ser rapidamente verificado. Na prática, a prova de primalidade por curvas elípticas é o mais rápido entre os testes de primalidade com garantia de uma resposta correta, mas sua análise de tempo de execução é baseada em argumentos heurísticos em vez de provas rigorosas. O teste de primalidade AKS possui uma complexidade de tempo matematicamente provada, mas, na prática, o método é mais lento que a prova por curvas elípticas. Esses métodos podem ser usados ​​para gerar grandes números primos aleatórios, gerando e testando números aleatórios até encontrar um que seja primo; ao fazer isso, um teste probabilístico mais rápido pode eliminar rapidamente a maioria dos números compostos antes que um algoritmo que garanta uma resposta correta seja usado para verificar se os números restantes são primos.
A tabela a seguir lista alguns desses testes. Seu tempo de execução é dado em termos de n, o número a ser testado e, para algoritmos probabilísticos, o número k de testes realizados. Além disso, ε é um número positivo arbitrariamente pequeno, e log é o logaritmo para uma base não especificada. A notação big-O significa que cada limite de tempo deve ser multiplicado por um fator constante para convertê-lo de unidades adimensionais para unidades de tempo; esse fator depende de detalhes de implementação, como o tipo de computador usado para executar o algoritmo, mas não dos parâmetros de entrada n e k.


### Algoritmos para tipos específicos e o maior primo conhecido
Além dos testes mencionados acima, que se aplicam a qualquer número natural, alguns números de formato especial podem ser testados quanto à primalidade mais rapidamente. Por exemplo, o teste de primalidade de Lucas–Lehmer pode determinar se um número de Mersenne (um a menos que uma potência de dois) é primo, deterministicamente, usando o mesmo tempo que uma única iteração do teste de Miller-Rabin. É por isso que desde 1992 (até outubro de 2024) o maior primo conhecido sempre foi um primo de Mersenne. Conjectura-se que existam infinitos primos de Mersenne.
A tabela a seguir apresenta os maiores números primos conhecidos de vários tipos. Alguns desses primos foram encontrados usando processamento distribuído. Em 2009, o projeto Great Internet Mersenne Prime Search recebeu um prêmio de 100 mil dólares pela primeira descoberta de um primo com pelo menos 10 milhões de dígitos. A Electronic Frontier Foundation também oferece 150 mil e 250 mil dólares para quem encontrar primos com pelo menos 100 milhões e 1 bilhão de dígitos, respectivamente.


### Fatoração de inteiros
Dado um número inteiro composto n, a tarefa de fornecer um ou mais de seus fatores primos é chamada de fatoração de n. É significativamente mais difícil do que o teste de primalidade, e, embora muitos algoritmos de fatoração sejam conhecidos, eles são mais lentos do que os métodos mais rápidos de teste de primalidade. A divisão por tentativa e o algoritmo rho de Pollard podem ser usados para encontrar fatores muito pequenos de n, e a fatoração de curva elíptica pode ser eficaz quando n tem fatores de tamanho moderado. Os métodos adequados para números arbitrariamente grandes que não dependem do tamanho de seus fatores incluem o crivo quadrático e o crivo do corpo de números generalizado. Assim como no teste de primalidade, há também algoritmos de fatoração que exigem que sua entrada tenha uma forma específica, incluindo o crivo do corpo de números específico. Em dezembro de 2019, o maior número conhecido por ter sido fatorado por um algoritmo de uso geral é o RSA-240, que tem 240 dígitos decimais (795 bits) e é o produto de dois primos grandes.
O algoritmo de Shor pode fatorar qualquer número inteiro em uma quantidade polinomial de etapas em um computador quântico. Entretanto, a tecnologia atual só pode executar esse algoritmo para números muito pequenos. Em outubro de 2012, o maior número que foi fatorado por um computador quântico que executa o algoritmo de Shor é 21.


### Outras aplicações computacionais
Vários algoritmos de criptografia de chave pública, como RSA e a troca de chaves de Diffie–Hellman, são baseados em grandes números primos (primos de 2048 bits são comuns). O RSA se baseia na suposição de que é muito mais fácil (ou seja, mais eficiente) realizar a multiplicação de dois números (grandes) x e y do que calcular x e y (assumindo que são coprimos) se apenas o produto xy for conhecido. A troca de chaves Diffie–Hellman se baseia no fato de que existem algoritmos eficientes para exponenciação modular (computando ab mod c), enquanto a operação reversa (o logaritmo discreto) é considerada um problema difícil.
Os números primos são usados com frequência em tabelas de dispersão. Por exemplo, o método original de Carter e Wegman para hashing universal baseava-se em funções hash de computação escolhendo funções lineares aleatórias no módulo de grandes números primos. Carter e Wegman generalizaram esse método para o hashing k-independente usando polinômios de grau mais alto, novamente no módulo de grandes números primos. Assim como na função de hash, os números primos são usados para definir o tamanho da tabela de dispersão em tabelas de dispersão baseadas em sondagem quadrática para garantir que a sequência de sondagem cubra toda a tabela.
Alguns métodos de soma de verificação são baseados na matemática dos números primos. Por exemplo, as somas de verificação usadas nos International Standard Book Numbers são definidas tomando-se o resto do número no módulo 11, um número primo. Como 11 é primo, esse método pode detectar erros de um único dígito e transposições de dígitos adjacentes. Outro método de soma de verificação, o Adler-32 [en], usa o módulo aritmético 65521, o maior número primo menor que 216. Os números primos também são usados em geradores de números pseudoaleatórios, incluindo geradores congruentes lineares e o Mersenne Twister.


## Outras aplicações
Os números primos são de importância central para a teoria dos números, mas também têm muitas aplicações em outras áreas da matemática, incluindo álgebra abstrata e geometria elementar. Por exemplo, é possível colocar um número primo de pontos em uma malha bidimensional de modo que não haja três pontos alinhados, ou de modo que cada triângulo formado por três dos pontos tenha uma área não nula. Outro exemplo é o critério de Eisenstein, um teste para saber se um polinômio é irredutível com base na divisibilidade de seus coeficientes por um número primo e seu quadrado.

O conceito de um número primo é tão importante que foi generalizado de diferentes maneiras em vários ramos da matemática. Em geral, "primo" indica minimalidade ou indecomponibilidade, em um sentido apropriado. Por exemplo, o corpo primo de um determinado corpo é seu menor subcorpo que contém 0 e 1. É o corpo dos números racionais ou um corpo finito com um número primo de elementos (daí o nome). Muitas vezes, um segundo significado adicional é pretendido com o uso da palavra primo: qualquer objeto pode ser decomposto, essencialmente de forma única, em seus componentes primos. Por exemplo, na teoria dos nós, um nó primo é um nó que não podem ser decompostos, no sentido de que não pode ser escrito como a soma conectada de dois nós não triviais. Qualquer nó pode ser expresso exclusivamente como uma soma conectada de nós primos. A decomposição prima de 3-variedades é outro exemplo desse tipo.
Além da matemática e da computação, os números primos têm possíveis conexões com a mecânica quântica e têm sido usados metaforicamente nas artes e na literatura. Eles também foram usados na biologia evolutiva para explicar os ciclos de vida das cigarras.


### Polígonos construtíveis e partições de polígonos
Os primos de Fermat são aqueles da forma

  
    
      
        
          F
          
            k
          
        
        =
        
          2
          
            
              2
              
                k
              
            
          
        
        +
        1
        ,
      
    
    {\displaystyle F_{k}=2^{2^{k}}+1,}
  

com k inteiro não negativo. Eles receberam esse nome em homenagem a Pierre de Fermat, que conjecturou que todos esses números são primos. Os primeiros cinco desses números — 3, 5, 17, 257 e 65 537 — são primos, mas F5 é composto, assim como todos os outros números de Fermat que foram verificados até 2017. Um n-ágono regular é construtível usando régua e compasso se, e somente se, os fatores primos ímpares de n (se houver) forem primos de Fermat distintos. Da mesma forma, um n-ágono regular pode ser construído usando régua, compasso e uma trissecção do ângulo se, e somente se, os fatores primos de n forem qualquer número de cópias de 2 ou 3, juntamente com um conjunto (possivelmente vazio) de primos de Pierpont [en] distintos, que são primos da forma 2a ⋅ 3b + 1.
É possível dividir qualquer polígono convexo em n polígonos convexos menores de mesma área e perímetro quando n é uma potência de um número primo, mas isso não é conhecido para outros valores de n.


### Mecânica quântica
Começando com o trabalho de Hugh Montgomery e Freeman Dyson na década de 1970, matemáticos e físicos especularam que as raízes da função zeta de Riemann estão conectados aos níveis de energia dos sistemas quânticos. Os números primos também são importantes na ciência da informação quântica, graças a estruturas matemáticas como bases mutuamente imparciais e medidas simétricas de valor positivo com operador positivo e informativamente completas.


### Biologia
A estratégia evolutiva usada pelas cigarras do gênero Magicicada faz uso de números primos. Esses insetos passam a maior parte de suas vidas como larvas subterrâneas. Eles só se tornam pupas e emergem de suas tocas depois de 7, 13 ou 17 anos, quando voam, se reproduzem e morrem depois de no máximo algumas semanas. Os biólogos teorizam que essas durações de ciclos de reprodução com números primos evoluíram para evitar que os predadores se sincronizem com esses ciclos. Por outro lado, os períodos de vários anos entre a floração das plantas de bambu são considerados números suaves, tendo apenas pequenos números primos em suas fatorações.


### Artes e literatura
Os números primos influenciaram muitos artistas e escritores. O compositor francês Olivier Messiaen usou os números primos para criar música amétrica por meio de "fenômenos naturais". Em obras como La Nativité du Seigneur (1935) e Quatre études de rythme (1949-1950), ele emprega simultaneamente temas com comprimentos dados por diferentes números primos para criar ritmos imprevisíveis: os primos 41, 43, 47 e 53 aparecem no terceiro estudo, "Neumes rythmiques". De acordo com Messiaen, essa maneira de compor foi "inspirada pelos movimentos da natureza, movimentos de durações livres e desiguais".
Em seu romance de ficção científica Contact, o cientista Carl Sagan sugeriu que a decomposição em números primos poderia ser usada como um meio de estabelecer planos de imagem bidimensionais em comunicações com alienígenas, uma ideia que ele havia desenvolvido informalmente com o astrônomo americano Frank Drake, em 1975. No romance The Curious Incident of the Dog in the Night-Time, de Mark Haddon, o narrador organiza as seções da história por números primos consecutivos como forma de transmitir o estado mental de seu personagem principal, um adolescente matematicamente talentoso com síndrome de Asperger. Os números primos são usados como metáfora para solidão e isolamento no romance The Solitude of Prime Numbers, de Paolo Giordano, no qual são retratados como "forasteiros" entre os números inteiros.


## Notas
## Referências
### Bibliografia
