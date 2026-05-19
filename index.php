<?php
/**
 * Servidor de Auditoría Onnet - PHP Nativo
 * 
 * Para ejecutar: php -S localhost:8000
 */

// Configuración de conexión a la base de datos (Tomada de carga_db.py)
$host = "localhost";
$port = "5432";
$dbname = "onnet_auditoria";
$user = "postgres";
$password = "admin123";

try {
    $dsn = "pgsql:host=$host;port=$port;dbname=$dbname";
    $pdo = new PDO($dsn, $user, $password, [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
} catch (PDOException $e) {
    $error_db = $e->getMessage();
}

?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auditoría Onnet - PHP Server</title>
    <style>
        body { font-family: sans-serif; margin: 20px; background-color: #f4f4f9; color: #333; }
        .container { max-width: 1200px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .status { padding: 10px; margin-bottom: 20px; border-radius: 4px; }
        .success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #3498db; color: white; }
        tr:hover { background-color: #f1f1f1; }
        .btn { display: inline-block; padding: 10px 15px; background: #3498db; color: white; text-decoration: none; border-radius: 4px; }
    </style>
</head>
<body>

<div class="container">
    <h1>🔎 Reporte de Auditoría (Conexión SQL)</h1>

    <?php if (isset($error_db)): ?>
        <div class="status error">
            <strong>Error de conexión:</strong> <?php echo $error_db; ?>
            <p>Asegúrate de que PostgreSQL esté corriendo y las credenciales sean correctas.</p>
        </div>
    <?php else: ?>
        <div class="status success">
            ✅ Conectado exitosamente a PostgreSQL (Base de datos: <?php echo $dbname; ?>)
        </div>

        <?php
        // Consulta simple a la tabla inyectada por carga_db.py
        $stmt = $pdo->query("SELECT * FROM cierres_contratista LIMIT 50");
        $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);
        ?>

        <h3>Últimos 50 Registros en Base de Datos</h3>
        <table>
            <thead>
                <tr>
                    <?php if (!empty($rows)): ?>
                        <?php foreach (array_keys($rows[0]) as $column): ?>
                            <th><?php echo htmlspecialchars($column); ?></th>
                        <?php endforeach; ?>
                    <?php endif; ?>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($rows as $row): ?>
                    <tr>
                        <?php foreach ($row as $value): ?>
                            <td><?php echo htmlspecialchars($value); ?></td>
                        <?php endforeach; ?>
                    </tr>
                <?php endforeach; ?>
                <?php if (empty($rows)): ?>
                    <tr><td colspan="100%">No hay datos disponibles. Ejecute <code>carga_db.py</code> primero.</td></tr>
                <?php endif; ?>
            </tbody>
        </table>
    <?php endif; ?>

    <p style="margin-top: 30px;">
        <small>Servidor local ejecutándose con PHP Nativo. Sin necesidad de XAMPP.</small>
    </p>
</div>

</body>
</html>
