import ustruct
def move_motor_fun():
    """ Function to move the motor during our calibration run"""

    while True:
        try:
            char_b = vcp.read(1)
            if char is not None:
                char = ustruct.unpack('b', char_b)

                if char == ord('w'):

                elif char == ord('a'):

                elif char == ord('s'):

                elif char == ord('d'):

                elif char == ord(' '):


                row = ustruct.unpack("i", row_b)
                #print_task.put(str(heading_setpoint_share.get()))


            col_b = vcp.read(4)
            if col_b != None:
                col = ustruct.unpack("i", col_b)
                #print_task.put("got new setpoints.   ")

            heading_setpoint_share.set(grid[row][col][0])
            pitch_setpoint_share.set(grid[row][col][1])

            trigger_ready_share.put(1)

        except ValueError:
            pass
        yield(0)
