import time
from threading import Thread

def matrix_multiply(a, b, result, i, j, k):
    result[i][j] += a[i][k] * b[k][j]

def test(num):
        matrix_a = [[1.1 for i in range(num)] for j in range(num)] 
        matrix_b = [[2.2 for i in range(num)] for j in range(num)]
        result = [[0.0 for i in range(num)] for j in range(num)]
        start = time.time()
        threads = []
        for i in range(len(matrix_a)):
            for j in range(len(matrix_b[0])):
                for k in range(len(matrix_b)):
                    thread = Thread(target=matrix_multiply, args=(matrix_a, matrix_b,  result, i, j, k))
                    thread.start()
                    threads.append(thread)
        for thread in threads:
            thread.join()
        end = time.time()
        print(f'Time taken: {end - start} seconds')
