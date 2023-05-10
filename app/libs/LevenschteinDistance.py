

def calculate_distance(s: str, t: str):
    N = len(s)
    M = len(t)

    matrix_distances = [[0]*M for i in range(N)]

    for i in range(N):
        for j in range(M):
            if min(i, j) == 0:
                matrix_distances[i][j] = max(i, j)
            else:
                x, y, z = matrix_distances[i - 1][j], matrix_distances[i][j - 1], matrix_distances[i - 1][j - 1]
                matrix_distances[i][j] = min(x, y, z)
                if s[i] != t[j]:
                    matrix_distances[i][j] += 1

    return matrix_distances[-1][-1]
