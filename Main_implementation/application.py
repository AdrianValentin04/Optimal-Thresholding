import localImplementation
import globalImplementation
import time

def runLocal():
    totalExecTime = 0
    print("Se ruleaza implementarea locala:")
    localSolver = localImplementation.LocalSolver()
    
    start_time = time.time()
    print("Se ruleaza etapa de training:")
    localSolver.localTrain()
    print("--- %s timp de executie ---" % (time.time() - start_time))
    totalExecTime += time.time() - start_time
    print("===============================")
    time.sleep(3)

    start_time = time.time()
    print("Se ruleaza etapa de validation:")
    localSolver.localValidation()
    print("--- %s timp de executie ---" % (time.time() - start_time))
    totalExecTime += time.time() - start_time
    print("===============================")
    time.sleep(3)

    start_time = time.time()
    print("Se ruleaza etapa de test:")
    localSolver.localTest()
    print("--- %s timp de executie ---" % (time.time() - start_time))
    totalExecTime += time.time() - start_time
    print("===============================")
    time.sleep(3)
    
    print("S-a ajuns la urmatoarele solutii:")
    for comb in localSolver.binarization.allCombinations:
        print(comb)

    print("--- %s timp de executie total ---" % totalExecTime)

def runGlobal():
    totalExecTime = 0
    print("Se ruleaza implementarea globala:")
    globalSolver = globalImplementation.GlobalSolver()

    start_time = time.time()
    print("Se ruleaza etapa de training:")
    globalSolver.globalTrain()
    print("--- %s timp de executie ---" % (time.time() - start_time))
    totalExecTime += time.time() - start_time
    print("===============================")
    time.sleep(3)

    start_time = time.time()
    print("Se ruleaza etapa de validation:")
    globalSolver.globalValidation()
    print("--- %s timp de executie ---" % (time.time() - start_time))
    totalExecTime += time.time() - start_time
    print("===============================")
    time.sleep(3)

    start_time = time.time()
    print("Se ruleaza etapa de test:")
    globalSolver.globalTest()
    print("--- %s timp de executie ---" % (time.time() - start_time))
    totalExecTime += time.time() - start_time
    print("===============================")
    time.sleep(3)

    print("--- %s timp de executie total ---" % totalExecTime)

def main():
    while True:
        mode = input("Alege implementarea dorita [global, local]: ")
        if mode == "local":
            runLocal()
            break
        elif mode == "global":
            runGlobal()
            break
        else:
            print("Nu e ce trebuie :(")

if __name__ == "__main__":
    main()