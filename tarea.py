def fibonacci(num, ant, cont):
    if(cont > 1):
        aux = ant
        num = ant + num
        ant = aux + num
        print(num, ant)
        fibonacci(num, ant, (cont - 1))
    
fibonacci(1,0,7)
