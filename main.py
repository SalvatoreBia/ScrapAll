import sys
from src import parser


if __name__ == '__main__':

    if (len(sys.argv)) == 2:
        filename = sys.argv[1].strip()

        myParser = parser.Parser('edge')
        with open(filename, 'r') as file:
            content = file.read()

            if (len(content)) > 0:
                myParser.set_script(content)
                myParser.parse_script()
                print(myParser.get_output_content())
