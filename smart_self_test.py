#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from system_cmd import system_cmd



#
# run smartctl --test
#
# to perform a disk smart self test.
#
def smart_self_test(device_filename,
                    device_type,
                    short=False,
                    long=False,
                    conveyance=False,
                    abort_test=False,
                    print_progress=False,
                    ):
    """
    @description:
    Perform disk self test.

    This program checks the electrical and mechanical performance,
    as well as the read/write performance of the disk. After the check some
    of offline S.M.A.R.T. attribute are updated.

    This program does detect S.M.A.R.T. enabled drive only. Not suitable for
    CD/DVD ROM drives, or removable USB Flash Drives.

    Option <short>, <long>, <conveyance> and <abort_test> cannot be used together.

    This function requires smartctl to run.
    SystemCmdException is raised if smartctl has encountered an error.
    

    @param device_filename@f: The drive device filename. (e.g. /dev/sda)
    @param device_type@d: The type of the device. (e.g. sat, ata...)
    @param short@S: Roughly scan the disk surface. (Up to two minutes)
    @param long@L: Scan the entire disk surface. (This may take several hours, depends on disk capacity)
    @param conveyance@C: Test to identify any damage(s) during transportation.
    @param abort_test@X: Abort a self-test.
    @param print_progress@P: Print status and progress%, and then exit.
    @param special_fx_kwargs: Additional options to be passed on to the function sumikko_func_begin.

    @retval self_test_status: A self-test status string. (TESTING or STOPPED)
    @retval progress_percent: A Progress %.
    """

    S = 1 if short else 0
    L = 1 if long else 0
    C = 1 if conveyance else 0
    X = 1 if abort_test else 0
    P = 1 if print_progress else 0

    if (S + L + C + X + P) > 1:
        raise Exception(
            "Option 'short', 'long', 'conveyance', 'abort_test' and 'print_progress' cannot be used together.")

    #/* smartctl -c shows self test running status */

    #
    # (during self testing...)
    # smartctl -c sample output
    #
    # smartctl 7.0 2018-12-30 r4883 [x86_64-linux-5.3.0-46-generic] (local build)
    # Copyright (C) 2002-18, Bruce Allen, Christian Franke, www.smartmontools.org
    #
    # === START OF READ SMART DATA SECTION ===
    #
    # Self-test execution status:     ( 242)  Self-test routine in progress...
    #                                         20% of test remaining.
    #

    #
    # (self test not run)
    # smartctl -c sample output
    #
    # smartctl 7.0 2018-12-30 r4883 [x86_64-linux-5.3.0-46-generic] (local build)
    # Copyright (C) 2002-18, Bruce Allen, Christian Franke, www.smartmontools.org
    #
    # === START OF READ SMART DATA SECTION ===
    # General SMART Values:
    # Offline data collection status: (0x82)  Offline data collection activity
    #                                         was completed without error.
    #                                         Auto Offline Data Collection: Enabled.
    # Self-test execution status:     (   0)  The previous self-test routine completed
    #                                         without error or no self-test has ever
    #                                         been run.
    #

    cmd = ["smartctl", "--capabilities", "--device",
           device_type, "--", device_filename,]
    
    unused, cmd_output, unused, unused = system_cmd(*cmd)

    #/* find a line begins with "Self-test execution status:" */
    cmd_output_lines = cmd_output.splitlines()

    self_text_status_line_found = False
    for j, line in enumerate(cmd_output_lines):
        line = line.lower()
        if line.startswith("self-test execution status:"):
            self_text_status_line_found = True
            break

    if not self_text_status_line_found:
        raise Exception(
            "Cannot not find a line from smartctl output: 'Self-test execution status:', smartctl may be modified")

    #/* go to next line */
    j = j + 1

    #/* line end with "of test remaining."
    # * If true, return "RUNNING", 100-percentage_remaining
    # */
    percentage = 100.0
    status = "NOT_RUNNING"
    line = cmd_output_lines[j]
    if not(abort_test) and line.endswith("of test remaining."):

        #/* get percentage_remaining */
        tmp = line.split("%", 1)
        percentage_remaining = float(tmp[0])

        #/* progress% = 100 - percentage_remaining */
        percentage = 100.0 - percentage_remaining
        status = "RUNNING"

    #/************************************************************************/

    #/* if not, do smart self-test */
    if status == "NOT_RUNNING" and (not print_progress):

        percentage = 0.0
        status = "RUNNING"
        smartctl_opts = []

        if short:
            smartctl_opts.extend(["--test", "short",])

        elif long:
            smartctl_opts.extend(["--test", "long",])

        elif conveyance:
            smartctl_opts.extend(["--test", "conveyance",])

        elif abort_test:
            smartctl_opts.extend(["--abort",])
            status = "NOT_RUNNING"

        #/* smartctl <smartctl_opts> --device <device_type> -- <device_filename> */
        cmd = []

        cmd.append("smartctl")
        cmd.extend(smartctl_opts)
        cmd.extend(["--device", device_type, "--", device_filename,])

        unused, unused, unused, unused = system_cmd(*cmd)

    return status, percentage  # CCCsumikko_func_end


if __name__ == '__main__':
    print(simple_argparse(smart_self_test, sys.argv[1:]))
