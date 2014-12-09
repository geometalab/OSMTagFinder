<script>
    window.testJsonP = function(data) {
      alert(data);
    };
</script>
 <script src="http://localhost:5000/api/suggest?query=pool&lang=de&callback=testJsonP"></script>