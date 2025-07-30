from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import glob
import os

class DirectorySearchInput(BaseModel):
    search_path: str = Field(..., description="Path pattern to search (e.g., 'features/**/*.feature', './*.py'). Supports recursive glob patterns like '**'.")

class DirectorySearchTool(BaseTool):
    name: str = "directory_search_tool"
    description: str = "Search for files and directories using a glob pattern. Use '**' for recursive searches."
    args_schema: Type[BaseModel] = DirectorySearchInput

    def _run(self, search_path: str) -> str:
        """Search for files and directories using a glob pattern."""
        try:
            print(f"DirectorySearchTool: Searching with glob pattern '{search_path}'")
            
            results = glob.glob(search_path, recursive=True)
            
            exclude_list = ["node_modules", ".git", ".venv", "venv", "__pycache__"]
            
            filtered_results = [
                p for p in results 
                if not any(excluded in p.split(os.sep) for excluded in exclude_list)
            ]

            found_files = []
            found_dirs = []

            for path in filtered_results:
                if os.path.isdir(path):
                    found_dirs.append(path)
                else:
                    found_files.append(path)

            output = f"Search Pattern: {search_path}\n"
            
            if not found_files and not found_dirs:
                output += "No files or directories found matching the pattern.\n"
            else:
                if found_dirs:
                    output += f"Found directories ({len(found_dirs)}):\n"
                    for dir_path in sorted(found_dirs):
                        output += f"  - {dir_path}\n"
                    output += "\n"
                
                if found_files:
                    output += f"Found files ({len(found_files)}):\n"
                    for file_path in sorted(found_files):
                        output += f"  - {file_path}\n"
            
            print(f"DirectorySearchTool: Found {len(found_files)} files and {len(found_dirs)} directories")
            return output
            
        except Exception as e:
            error_msg = f"Error searching with glob: {str(e)}"
            print(f"DirectorySearchTool: {error_msg}")
            return error_msg 