import os
import subprocess
from fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP("amass-mcp")


@mcp.tool()
def amass(
    subcommand: str,
    domain: str = "",
    intel_whois: bool = False,
    intel_organization: str = "",
    enum_type: str = "active",
    enum_brute: bool = False,
    enum_brute_wordlist: str = ""
) -> str:
    """
    Advanced subdomain enumeration and reconnaissance tool using OWASP Amass.
    
    Args:
        subcommand: Specify the Amass operation mode - 'intel' for gathering intelligence about target domains, 'enum' for subdomain enumeration and network mapping
        domain: Target domain to perform reconnaissance against (e.g., example.com)
        intel_whois: Whether to include WHOIS data in intelligence gathering (true/false)
        intel_organization: Organization name to search for during intelligence gathering (e.g., 'Example Corp')
        enum_type: Enumeration approach type - 'active' includes DNS resolution, 'passive' only uses third-party sources
        enum_brute: Whether to perform brute force subdomain discovery (true/false)
        enum_brute_wordlist: Path to custom wordlist file for brute force operations
    """
    if subcommand not in ["enum", "intel"]:
        return f"Error: subcommand must be 'enum' or 'intel', got '{subcommand}'"
    
    amass_args = ["amass", subcommand]
    
    if subcommand == "enum":
        if not domain:
            return "Error: Domain parameter is required for 'enum' subcommand"
        
        amass_args.extend(["-d", domain])
        
        if enum_type == "passive":
            amass_args.append("-passive")
        
        if enum_brute:
            amass_args.append("-brute")
            if enum_brute_wordlist:
                amass_args.extend(["-w", enum_brute_wordlist])
    
    elif subcommand == "intel":
        if not domain and not intel_organization:
            return "Error: Either domain or organization parameter is required for 'intel' subcommand"
        
        if domain:
            amass_args.extend(["-d", domain])
            if not intel_whois:
                return "Error: For domain parameter, whois is required. Set intel_whois=true"
        
        if intel_organization:
            amass_args.extend(["-org", intel_organization])
        
        if intel_whois:
            amass_args.append("-whois")
    
    command_str = " ".join(amass_args)
    print(f"Executing: {command_str}")
    
    try:
        result = subprocess.run(
            amass_args,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\n\nStderr:\n{result.stderr}"
        
        if result.returncode != 0:
            return f"Amass exited with code {result.returncode}.\nOutput: {output}\nCommand: {command_str}"
        
        if not output.strip():
            return f"Amass completed successfully but returned no output.\nCommand: {command_str}"
        
        return output
        
    except subprocess.TimeoutExpired:
        return f"Error: Amass command timed out after 300 seconds.\nCommand: {command_str}"
    except FileNotFoundError:
        return f"Error: Amass binary not found. Ensure amass is installed.\nCommand: {command_str}"
    except Exception as e:
        return f"Error executing amass: {str(e)}\nCommand: {command_str}"


# Run the server with SSE transport
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    
    mcp.run(
        transport="sse",
        host="0.0.0.0",
        port=port,
        path="/mcp"
    )
