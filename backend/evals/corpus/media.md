# Média aritmética

Arquitas de Tarento, um matemático pitagórico que viveu por volta de 400 a.C., definiu que existiam três tipos de média. 
Um número é a média aritmética de dois outros quando o excesso do primeiro para o segundo é igual ao excesso do segundo para o terceiro, a média geométrica quando a proporção do segundo para o terceiro é igual à proporção do primeiro para o segundo, e a média harmônica quando a quantidade que o primeiro excede o segundo em relação ao primeiro é igual à quantidade que o segundo excede o terceiro em relação ao terceiro; em notação moderna, sendo o primeiro x, o segundo m e o terceiro y (x > m > y > 0):

média aritmética: 
  
    
      
        x
        −
        m
        =
        m
        −
        y
      
    
    {\displaystyle x-m=m-y}
  

média geométrica: 
  
    
      
        
          
            m
            y
          
        
        =
        
          
            x
            m
          
        
      
    
    {\displaystyle {\frac {m}{y}}={\frac {x}{m}}}
  

média harmônica: 
  
    
      
        
          
            
              x
              −
              m
            
            x
          
        
        =
        
          
            
              m
              −
              y
            
            y
          
        
      
    
    {\displaystyle {\frac {x-m}{x}}={\frac {m-y}{y}}}
  

Após algumas transformações, chega-se às fórmulas:

média aritmética: 
  
    
      
        m
        =
        
          
            
              x
              +
              y
            
            2
          
        
      
    
    {\displaystyle m={\frac {x+y}{2}}}
  

média geométrica: 
  
    
      
        m
        =
        
          
            x
            y
          
        
      
    
    {\displaystyle m={\sqrt {xy}}}
  

média harmônica: 
  
    
      
        
          
            1
            m
          
        
        =
        
          
            1
            2
          
        
        (
        
          
            1
            x
          
        
        +
        
          
            1
            y
          
        
        )
      
    
    {\displaystyle {\frac {1}{m}}={\frac {1}{2}}({\frac {1}{x}}+{\frac {1}{y}})}
  


## Tipos de média aritmética
Há dois tipos de média aritmética - simples ou ponderada.


### Média aritmética simples
A média aritmética simples é a mais utilizada no nosso dia-a-dia. É obtida dividindo-se a soma das observações pelo número delas. É um quociente geralmente representado pelo símbolo 
  
    
      
        
          
            
              x
              ¯
            
          
        
        .
      
    
    {\displaystyle {\bar {x}}.}
  
 
Se tivermos uma série de n valores de uma variável x, a média aritmética simples será determinada pela expressão:

  
    
      
        
          
            
              x
              ¯
            
          
        
        =
        
          
            
              
                x
                
                  1
                
              
              +
              
                x
                
                  2
                
              
              +
              .
              .
              .
              .
              +
              
                x
                
                  n
                
              
            
            n
          
        
        =
        
          
            1
            n
          
        
        
          ∑
          
            i
            =
            1
          
          
            n
          
        
        
          
            x
            
              i
            
          
        
      
    
    {\displaystyle {\bar {x}}={\frac {x_{1}+x_{2}+....+x_{n}}{n}}={1 \over n}\sum _{i=1}^{n}{x_{i}}}
  


### Média aritmética ponderada
Consideremos uma coleção formada por n números: 
  
    
      
        
          x
          
            1
          
        
        ,
        
          x
          
            2
          
        
        ,
        …
        ,
        
          x
          
            n
          
        
        ,
      
    
    {\displaystyle x_{1},x_{2},\ldots ,x_{n},}
  
 de forma que cada um esteja sujeito a um peso, respectivamente, indicado por: 
  
    
      
        
          p
          
            1
          
        
        ,
        
          p
          
            2
          
        
        ,
        …
        ,
        
          p
          
            n
          
        
        .
      
    
    {\displaystyle p_{1},p_{2},\ldots ,p_{n}.}
  
 A média aritmética ponderada desses n números é a soma dos produtos de cada um multiplicados por seus respectivos pesos, dividida pela soma dos pesos, isto é:

  
    
      
        
          
            
              p
              ¯
            
          
        
        =
        
          
            
              
                x
                
                  1
                
              
              
                p
                
                  1
                
              
              +
              
                x
                
                  2
                
              
              
                p
                
                  2
                
              
              +
              .
              .
              .
              .
              +
              
                x
                
                  n
                
              
              
                p
                
                  n
                
              
            
            
              
                p
                
                  1
                
              
              +
              
                p
                
                  2
                
              
              +
              .
              .
              .
              .
              +
              
                p
                
                  n
                
              
            
          
        
        =
        
          
            
              
                ∑
                
                  i
                  =
                  1
                
                
                  n
                
              
              
                
                  x
                  
                    i
                  
                
                
                  p
                  
                    i
                  
                
              
            
            
              
                ∑
                
                  i
                  =
                  1
                
                
                  n
                
              
              
                
                  p
                  
                    i
                  
                
              
            
          
        
      
    
    {\displaystyle {\bar {p}}={\frac {x_{1}p_{1}+x_{2}p_{2}+....+x_{n}p_{n}}{p_{1}+p_{2}+....+p_{n}}}={\frac {\sum _{i=1}^{n}{x_{i}p_{i}}}{\sum _{i=1}^{n}{p_{i}}}}}
  

Obviamente, a média aritmética e a média ponderada podem ser generalizadas para estruturas algébricas mais complexas; a única restrição é que a soma dos pesos seja um número invertível (em particular, não pode ser zero).
Caso todos os valores 
  
    
      
        x
      
    
    {\displaystyle x}
  
 tenham o mesmo peso 
  
    
      
        p
      
    
    {\displaystyle p}
  
, podemos simplificar a média ponderada em uma média simples isolando 
  
    
      
        p
      
    
    {\displaystyle p}
  
:

  
    
      
        
          
            
              p
              ¯
            
          
        
        =
        
          
            
              
                x
                
                  1
                
              
              
                p
                
                  1
                
              
              +
              
                x
                
                  2
                
              
              
                p
                
                  2
                
              
              +
              .
              .
              .
              .
              +
              
                x
                
                  n
                
              
              
                p
                
                  n
                
              
            
            
              
                p
                
                  1
                
              
              +
              
                p
                
                  2
                
              
              +
              .
              .
              .
              .
              +
              
                p
                
                  n
                
              
            
          
        
        =
        
          
            
              
                ∑
                
                  i
                  =
                  1
                
                
                  n
                
              
              
                
                  x
                  
                    i
                  
                
                
                  p
                  
                    i
                  
                
              
            
            
              
                ∑
                
                  i
                  =
                  1
                
                
                  n
                
              
              
                
                  p
                  
                    i
                  
                
              
            
          
        
      
    
    {\displaystyle {\bar {p}}={\frac {x_{1}p_{1}+x_{2}p_{2}+....+x_{n}p_{n}}{p_{1}+p_{2}+....+p_{n}}}={\frac {\sum _{i=1}^{n}{x_{i}p_{i}}}{\sum _{i=1}^{n}{p_{i}}}}}
  

  
    
      
        
          
            
              p
              ¯
            
          
        
        =
        
          
            
              
                ∑
                
                  i
                  =
                  1
                
                
                  n
                
              
              
                
                  x
                  
                    i
                  
                
                
                  p
                  
                    i
                  
                
              
            
            
              
                ∑
                
                  i
                  =
                  1
                
                
                  n
                
              
              
                
                  p
                  
                    i
                  
                
              
            
          
        
        =
        
          
            
              
                ∑
                
                  i
                  =
                  1
                
                
                  n
                
              
              
                
                  x
                  
                    i
                  
                
                p
              
            
            
              
                ∑
                
                  i
                  =
                  1
                
                
                  n
                
              
              
                p
              
            
          
        
        =
        
          
            
              p
              ×
              
                ∑
                
                  i
                  =
                  1
                
                
                  n
                
              
              
                
                  x
                  
                    i
                  
                
              
            
            
              n
              ×
              p
            
          
        
        =
        
          
            1
            n
          
        
        
          ∑
          
            i
            =
            1
          
          
            n
          
        
        
          
            x
            
              i
            
          
        
      
    
    {\displaystyle {\bar {p}}={\frac {\sum _{i=1}^{n}{x_{i}p_{i}}}{\sum _{i=1}^{n}{p_{i}}}}={\frac {\sum _{i=1}^{n}{x_{i}p}}{\sum _{i=1}^{n}{p}}}={\frac {p\times \sum _{i=1}^{n}{x_{i}}}{n\times p}}={\frac {1}{n}}\sum _{i=1}^{n}{x_{i}}}
  


## Exemplos
Um aluno tirou as notas 5, 7, 9 e 10 em quatro provas. A sua média será 
  
    
      
        
          
            
              5
              +
              7
              +
              9
              +
              10
            
            4
          
        
        =
        7
        ,
        75
      
    
    {\displaystyle {\frac {5+7+9+10}{4}}=7,75}
  
 ou seja 
  
    
      
        
          
            31
            4
          
        
        =
        7
        ,
        75
      
    
    {\displaystyle {\frac {31}{4}}=7,75}
  

Um aluno fez um teste (peso 1) e uma prova (peso 2), tirando 10 no teste e 4 na prova. A sua média (ponderada) será 
  
    
      
        
          
            
              10
              ⋅
              1
              +
              4
              ⋅
              2
            
            
              1
              +
              2
            
          
        
        =
        
          
            
              10
              +
              8
            
            3
          
        
        =
        6.
      
    
    {\displaystyle {\frac {10\cdot 1+4\cdot 2}{1+2}}={\frac {10+8}{3}}=6.}
  
 Logo, o resultado da média aritmética ponderada para este exemplo é 6.  Se o teste e a prova tivessem mesmo peso, e não importa qual o valor do peso, importando apenas a relação entre os pesos, a média ponderada aritmética seria sempre 7.  Isto é, se o aluno fizesse um teste (peso 3) e uma prova (peso 3), obtendo respectivamente a mesma pontuação anterior 10 e 4, teríamos: 
  
    
      
        
          
            
              10
              ⋅
              3
              +
              4
              ⋅
              3
            
            
              3
              +
              3
            
          
        
        =
        
          
            
              30
              +
              12
            
            6
          
        
        =
        7.
      
    
    {\displaystyle {\frac {10\cdot 3+4\cdot 3}{3+3}}={\frac {30+12}{6}}=7.}
  
 O resultado para pesos iguais será sempre "7".  Veja: 
  
    
      
        
          
            
              30
              +
              12
            
            6
          
        
        =
        7.
      
    
    {\displaystyle {\frac {30+12}{6}}=7.}
  

Um triângulo no plano tem vértices dados pelas coordenadas cartesianas (2, 1), (4, -1) e (3, 6). O seu baricentro é a média dos vértices, ou seja 
  
    
      
        (
        3
        ,
        2
        )
        .
      
    
    {\displaystyle (3,2).}
  


## Ver também
Média biquadrática
Média cúbica
Média geométrica
Média harmônica
Média quadrática
Mediana
Moda
Valor esperado


## Notas
## Referências
