<!DOCTYPE html>
<html lang="es">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>GIMM - Socios</title>
</head>

<body>

    <h1>GIMM - Lista de Socios</h1>

    <hr>

    {% if socios %}

        <table border="1">

            <thead>
                <tr>
                    <th>ID</th>
                    <th>Nombres</th>
                    <th>Apellidos</th>
                    <th>Cédula</th>
                    <th>Teléfono</th>
                    <th>Email</th>
                    <th>Activo</th>
                </tr>
            </thead>

            <tbody>

                {% for socio in socios %}

                    <tr>
                        <td>{{ socio.id }}</td>
                        <td>{{ socio.nombres }}</td>
                        <td>{{ socio.apellidos }}</td>
                        <td>{{ socio.cedula }}</td>
                        <td>{{ socio.telefono }}</td>
                        <td>{{ socio.email }}</td>
                        <td>{{ socio.activo }}</td>
                    </tr>

                {% endfor %}

            </tbody>

        </table>

    {% else %}

        <p>No existen socios registrados.</p>

    {% endif %}

</body>

</html>