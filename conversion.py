import matplotlib.pyplot as plt
import pandas as pd

def AcelACoor(ax, ay, az):

    dt = 0.01

    # Inicialización de variables
    vx, vy, vz = 0.0, 0.0, 0.0
    x, y, z = 0.0, 0.0, 0.0

    positions_x = [x]
    positions_y = [y]
    positions_z = [z]

    # Integración numérica para calcular posiciones
    for a_x, a_y, a_z in zip(ax, ay, az):
        vx += a_x * dt
        vy += a_y * dt
        vz += a_z * dt

        x += vx * dt
        y += vy * dt
        z += vz * dt

        positions_x.append(x)
        positions_y.append(y)
        positions_z.append(z)

        """
        df = pd.DataFrame({
        'Columna1': positions_x,
        'Columna2': positions_y,
        'Columna3': positions_z
        })
        """

    return positions_x, positions_y, positions_z

    """
    # Guardar el DataFrame en un archivo CSV
    df.to_csv('output.csv', index=False)
    
    # Resultados
    for i in range(len(positions_x)):
        print(f'X: {positions_x[i]:.10f}')
        print(f'Y: {positions_y[i]:.10f}')
        print(f'Z: {positions_z[i]:.10f}')
        print()

    # Visualización de los datos de aceleración y posiciones
    plt.figure(figsize=(12, 8))

    plt.subplot(3, 2, 1)
    plt.plot(ax, label='Aceleración en X')
    plt.legend()
    plt.subplot(3, 2, 2)
    plt.plot(positions_x, label='Posición en X')
    plt.legend()

    plt.subplot(3, 2, 3)
    plt.plot(ay, label='Aceleración en Y')
    plt.legend()
    plt.subplot(3, 2, 4)
    plt.plot(positions_y, label='Posición en Y')
    plt.legend()

    plt.subplot(3, 2, 5)
    plt.plot(az, label='Aceleración en Z')
    plt.legend()
    plt.subplot(3, 2, 6)
    plt.plot(positions_z, label='Posición en Z')
    plt.legend()

    plt.tight_layout()
    plt.show()
    """