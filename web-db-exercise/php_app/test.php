<?php
    $conn = new mysqli("dbcontainer", "example_user", "mysql", "example", "3306");
    $res = $conn->query("SELECT * FROM professor");
    
    while ($row = $res->fetch_assoc()):
?>
<div>
    <?= $row["first_name"] ?>
</div>
<?php
    endwhile;
    $conn->close();
?>
