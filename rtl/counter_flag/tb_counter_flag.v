`timescale 1ns/1ns

module tb_counter_flag();

    initial begin
        $dumpfile("counter_flag.vcd");
        $dumpvars(0, tb_counter_flag);
    end

    reg sys_clk;
    reg sys_rst_n;

    wire led_out;

    initial begin
        sys_clk = 1'b1;
        sys_rst_n <= 1'b0;
        #20
        sys_rst_n <= 1'b1;
        
        // Wait....
        #5000
        $finish;
    end

    always #10 sys_clk = ~sys_clk;

    counter_flag
    #(
        .CNT_MAX(25'd24)
    )
    counter_flag_inst(
        .sys_clk(sys_clk),
        .sys_rst_n(sys_rst_n),

        .led_out(led_out)
    );

endmodule
