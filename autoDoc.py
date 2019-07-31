# Objective: Write a function to extract docstrings from a given python function and output them in a new pdf file

def aDoc(ListFuncNames):
    f = open("docStrings.txt","w+") # Creates new file
    f.write('Here is a compilation of the doc-strings from the given list of functions. \n\n') # Adding first line to output file
    # Loop through each function, extacting the docstrings and adding them to the output file 
    index = 0
    for item in ListFuncNames:
        string = item.__doc__
        name = ListFuncNames[index]
        f.write('Function: ' + str(name))
        f.write(string + '\n')
        index += 1
    f.close()

# end of aDoc
