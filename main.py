
import CommandLine
import File
import UserDB

if __name__ == "__main__":
    shell = CommandLine.CLI(File.FileManager(), UserDB.UserManager())
    shell.main_loop()