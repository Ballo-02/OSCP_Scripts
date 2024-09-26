class RequestToPythonScript:
    def __init__(self, burp_request):
        self.burp_request = burp_request
        self.method = None
        self.url = None
        self.headers = {}
        self.data = None

    def parse_request(self):
        """Parse the Burp Suite request and extract the method, URL, headers, and data."""
        lines = self.burp_request.strip().split("\n")
        
        # First line contains the method and URL
        request_line = lines[0].split()
        self.method = request_line[0]  # GET, POST, etc.
        self.url = request_line[1]     # URL
        
        # Headers start after the request line and go until an empty line
        headers_done = False
        for line in lines[1:]:
            if line.strip() == "":  # Blank line indicates the end of headers
                headers_done = True
                continue

            if not headers_done:
                # Extract headers
                key, value = line.split(":", 1)
                self.headers[key.strip()] = value.strip()
            else:
                # Anything after headers is the body (for POST requests)
                self.data = line.strip()

    def generate_script(self, output_file):
        """Generate the Python script with hardcoded values."""
        # Start of the script
        script_content = f"""import requests

url = "{self.url}"
headers = {{
"""

        # Adding each header on a new line
        for key, value in self.headers.items():
            script_content += f"    '{key}': '{value}',\n"

        script_content += "}\n\n"

        # Add POST data if present
        if self.method == "POST" and self.data:
            script_content += f"data = '''{self.data}'''\n\n"

        # Add the request method
        if self.method == "POST":
            script_content += "response = requests.post(url, headers=headers, data=data)\n"
        else:
            script_content += "response = requests.get(url, headers=headers)\n"

        # Add response output handling
        script_content += """
if response.status_code == 200:
    print(response.text)
else:
    print(f"Request failed with status: {response.status_code}")
"""

        # Write the generated script to a file
        with open(output_file, "w") as f:
            f.write(script_content)
        print(f"Python script saved to {output_file}")
        
# Usage example
if __name__ == "__main__":
    burp_request = '''
    GET /example HTTP/1.1
    Host: example.com
    User-Agent: Mozilla/5.0
    Content-Type: application/x-www-form-urlencoded
    Accept: */*
    Content-Length: 27
    
    key1=value1&key2=value2
    '''
    
    # Create an instance and parse the request
    converter = RequestToPythonScript(burp_request)
    converter.parse_request()
    
    # Generate a Python script with hardcoded information
    output_file = "generated_request_script.py"
    converter.generate_script(output_file)
