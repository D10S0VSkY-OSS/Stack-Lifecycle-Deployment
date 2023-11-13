// script.js
function downloadTFVars(element) {
  // Retrieve the data-variables content, which is a string representation of a Python dictionary
  var data = element.getAttribute('data-variables');

  // Log the data for debugging
  console.log('Data-variables content:', data);

  // Convert and format the string to a pretty-printed JSON string
  try {
    var jsonString = data
      .replace(/'/g, '"') // Replace single quotes with double quotes
      .replace(/False/g, 'false') // Replace Python's False with JavaScript's false
      .replace(/True/g, 'true') // Replace Python's True with JavaScript's true
      .replace(/None/g, 'null'); // Replace Python's None with JavaScript's null

    // Parse and re-stringify with indentation for pretty-printing
    var formattedJsonString = JSON.stringify(JSON.parse(jsonString), null, 2);

    // Download the formatted JSON string as a blob
    var blob = new Blob([formattedJsonString], { type: 'application/json' });
    var url = URL.createObjectURL(blob);

    // Create a link, trigger a download, and clean up
    var a = document.createElement('a');
    a.download = 'terraform.tfvars.json';
    a.href = url;
    document.body.appendChild(a);
    a.click();
    URL.revokeObjectURL(url);
    document.body.removeChild(a);
  } catch (error) {
    console.error('Error converting dictionary string to JSON:', error);
  }
}
