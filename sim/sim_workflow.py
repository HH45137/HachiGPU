import os
import sys
import subprocess
import argparse
from pathlib import Path


class SimWorkflow:
    
    def __init__(self):
        self.rtl_dir = Path("../rtl")
        self.sim_dir = Path(".")
        
        if (sys.platform != 'win32'):
            self.tools = {
                'iverilog': 'iverilog',
                'vvp': 'vvp',
                'gtkwave': 'gtkwave'
                }
        else:
            self.tools = {
                'iverilog': 'iverilog.exe',
                'vvp': 'vvp.exe',
                'gtkwave': 'gtkwave.exe'
            }

        self.name = None


    def compile(self, top_module, src_files, output_name):
        print(f"Compiling {top_module}...")
        
        cmd = [self.tools['iverilog'], '-o', f"{output_name}.vvp", '-s', top_module]
                
        cmd.extend(src_files)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✓ Compilation successful: {output_name}.vvp")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Compilation failed:")
            print(e.stderr)
            return False


    def simulator(self, vvp_file, vcd_file):
        print(f"Run simulation {vvp_file}...")
        
        # Setup vcd file output
        os.environ['dumpfile'] = vcd_file
        
        try:
            result = subprocess.run([self.tools['vvp'], '-n', vvp_file],
                                    capture_output=True, text=True, check=True)
            print(f"✓ Simulation completed, waveform file generated: {vcd_file}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Simulation failed:")
            print(e.stderr)
            return False


    def view_waveform(self, vcd_file):
        if not os.path.exists(vcd_file):
            print(f"✗ Waveform file is not found: {vcd_file}")
            return False
            
        print(f"Open waveform file: {vcd_file}")
        try:
            subprocess.Popen([self.tools['gtkwave'], vcd_file])
            return True
        except Exception as e:
            print(f"✗ Can't open waveform file: {e}")
            return False


    def clean(self):
        print("Clean up the generated files...")
        extensions = ['.vvp', '.vcd', '.lst', '.log']
        
        for ext in extensions:
            for file in self.sim_dir.glob(f"*{ext}"):
                file.unlink()
                print(f"Remove: {file}")
        
        print("✓ Clean completed.")
    
    
    def get_name(self):
        print(self.name)
    
    
    def run(self):
        if not self.name:
            print("✗ Error: Module name is not set")
            return False
            
        base_name = self.name
        tb_name = f'tb_{self.name}'
        v_name = f'{self.name}'
        
        # 构建文件路径
        tb_file = self.rtl_dir / base_name / f"{tb_name}.v"
        v_file = self.rtl_dir / base_name / f"{v_name}.v"
        
        # 检查文件是否存在
        if not tb_file.exists():
            print(f"✗ Testbench file not found: {tb_file}")
            return False
        if not v_file.exists():
            print(f"✗ Module file not found: {v_file}")
            return False
        
        src_files = [str(tb_file), str(v_file)]
        vvp_name = tb_name
        vcd_name = f"{v_name}.vcd"
        
        if not self.compile(tb_name, src_files, vvp_name):
            return False
        
        if not self.simulator(f"{vvp_name}.vvp", vcd_name):
            return False
        
        return True
    
    
    def view(self):
        self.view_waveform(f"{self.name}.vcd")


def main():
    parser = argparse.ArgumentParser(description='FPGA RTL simulator tool')
    parser.add_argument('-m', '--module', default=None, help='The module to be simulated')
    parser.add_argument('-v', '--view', action='store_true', default=False, help='View the waveform graph immediately')
    parser.add_argument('-c', '--clean', action='store_true', default=False, help='Clean up generated files')
    
    args = parser.parse_args()
    
    sim = SimWorkflow()
    
    if args.clean:
        sim.clean()
    elif args.module != None:
        sim.name = args.module
        success = sim.run()
        if success and args.view:
            sim.view()
    else:
        print("✗ Error: No module specified. Use -m or --module to specify the module name.")
        parser.print_help()


if __name__ == '__main__':
    main()