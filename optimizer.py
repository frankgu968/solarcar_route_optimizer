import copy
import multiprocessing
import numpy as np

import matplotlib.pyplot as plt
from deap import base
from deap import creator
from deap import tools
from deap.algorithms import varAnd

import config
import world

if config.SHOW_PLOTS:
    plt.ion()
    fig, ax = plt.subplots(1, 2)    # 1 row, 2 column figure


def evalOneMax(individual):
    # TODO: Implement cost function with all the mathematical constraints
    fitness = world.simulate(individual)
    return fitness,


def cxTwoPointCopy(ind1, ind2):
    size = len(ind1)
    cxpoint1 = np.random.randint(1, size)
    cxpoint2 = np.random.randint(1, size - 1)
    if cxpoint2 >= cxpoint1:
        cxpoint2 += 1
    else:  # Swap the two cx points
        cxpoint1, cxpoint2 = cxpoint2, cxpoint1

    ind1[cxpoint1:cxpoint2], ind2[cxpoint1:cxpoint2] \
        = ind2[cxpoint1:cxpoint2].copy(), ind1[cxpoint1:cxpoint2].copy()

    return ind1, ind2


def optimize():

    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))  # Minimize the fitness function
    creator.create("Individual", np.ndarray, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()

    toolbox.register("attr_bool", np.random.randint, -100, 100)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, n=len(world.steps))
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", evalOneMax)
    toolbox.register("mate", cxTwoPointCopy)
    toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
    toolbox.register("select", tools.selTournament, tournsize=3)

    if config.GA_MULTITHREAD:
        pool = multiprocessing.Pool()
        toolbox.register("map", pool.map)

    pop = toolbox.population(n=config.GA_POP_NUM)

    # Numpy equality function (operators.eq) between two arrays returns the
    # equality element wise, which raises an exception in the if similar()
    # check of the hall of fame. Using a different equality function like
    # numpy.array_equal or numpy.allclose solve this issue.
    hof = tools.HallOfFame(config.GENERATIONAL_SURVIVAL, similar=np.allclose)

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)

    run(pop, toolbox, cxpb=0.5, mutpb=0.5, ngen=config.GA_GEN_NUM, stats=stats,
        halloffame=hof)

    return pop, stats, hof


# Based on eaSimple from the deap.algorithms package
def run(population, toolbox, cxpb, mutpb, ngen, stats=None,
             halloffame=None, verbose=__debug__):
    """This algorithm reproduce the simplest evolutionary algorithm as
    presented in chapter 7 of [Back2000]_.

    :param population: A list of individuals.
    :param toolbox: A :class:`~deap.base.Toolbox` that contains the evolution
                    operators.
    :param cxpb: The probability of mating two individuals.
    :param mutpb: The probability of mutating an individual.
    :param ngen: The number of generation.
    :param stats: A :class:`~deap.tools.Statistics` object that is updated
                  inplace, optional.
    :param halloffame: A :class:`~deap.tools.HallOfFame` object that will
                       contain the best individuals, optional.
    :param verbose: Whether or not to log the statistics.
    :returns: The final population and a :class:`~deap.tools.Logbook`
              with the statistics of the evolution.

    The algorithm takes in a population and evolves it in place using the
    :meth:`varAnd` method. It returns the optimized population and a
    :class:`~deap.tools.Logbook` with the statistics of the evolution (if
    any). The logbook will contain the generation number, the number of
    evalutions for each generation and the statistics if a
    :class:`~deap.tools.Statistics` if any. The *cxpb* and *mutpb* arguments
    are passed to the :func:`varAnd` function. The pseudocode goes as follow
    ::

        evaluate(population)
        for g in range(ngen):
            population = select(population, len(population))
            offspring = varAnd(population, toolbox, cxpb, mutpb)
            evaluate(offspring)
            population = offspring

    As stated in the pseudocode above, the algorithm goes as follow. First, it
    evaluates the individuals with an invalid fitness. Second, it enters the
    generational loop where the selection procedure is applied to entirely
    replace the parental population. The 1:1 replacement ratio of this
    algorithm **requires** the selection procedure to be stochastic and to
    select multiple times the same individual, for example,
    :func:`~deap.tools.selTournament` and :func:`~deap.tools.selRoulette`.
    Third, it applies the :func:`varAnd` function to produce the next
    generation population. Fourth, it evaluates the new individuals and
    compute the statistics on this population. Finally, when *ngen*
    generations are done, the algorithm returns a tuple with the final
    population and a :class:`~deap.tools.Logbook` of the evolution.

    .. note::

        Using a non-stochastic selection method will result in no selection as
        the operator selects *n* individuals from a pool of *n*.

    This function expects the :meth:`toolbox.mate`, :meth:`toolbox.mutate`,
    :meth:`toolbox.select` and :meth:`toolbox.evaluate` aliases to be
    registered in the toolbox.

    .. [Back2000] Back, Fogel and Michalewicz, "Evolutionary Computation 1 :
       Basic Algorithms and Operators", 2000.
    """
    logbook = tools.Logbook()
    logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in population if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    if halloffame is not None:
        halloffame.update(population)

    record = stats.compile(population) if stats else {}
    logbook.record(gen=0, nevals=len(invalid_ind), **record)
    if verbose:
        print logbook.stream

    # Begin the generational process
    for gen in range(1, ngen + 1):
        # Select the next generation individuals
        offspring = toolbox.select(population, len(population))

        # Vary the pool of individuals
        offspring = varAnd(offspring, toolbox, cxpb, mutpb)

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Update the hall of fame with the generated individuals
        if halloffame is not None:
            halloffame.update(offspring)

        # Plot the best individual (if enabled)
        if config.SHOW_PLOTS:
            plotData(halloffame[0], [x[0] for x in fitnesses], gen)

        # Replace the current population by the offspring
        population[:] = offspring

        # Append the current generation statistics to the logbook
        record = stats.compile(population) if stats else {}
        logbook.record(gen=gen, nevals=len(invalid_ind), **record)
        if verbose:
            print logbook.stream

    return population, logbook


def plotData(hof, popFitnesses, generation):
    # Run the simulation with the best individual again
    tempSolarCar = copy.deepcopy(world.solarCar)
    tempWorld = copy.deepcopy(world.steps)

    speeds = []
    axis = []
    inclination = []
    soc = []

    for index, stp in enumerate(tempWorld):
        stp.pbattExp = 250.  # DEBUG: Make sure this value is higher than the rolling resistance value; or the mathematics may fail!
        stp.pbatt = stp.pbattExp + hof[index]
        stp.advanceStep(tempSolarCar)

        # Copy state variables
        if index < len(tempWorld) - 1:
            tempWorld[index + 1].eTime = stp.eTime
            tempWorld[index + 1].gTime = stp.gTime
            tempWorld[index + 1].speed = stp.speed
            tempWorld[index + 1].battSoC = stp.battSoC

        # Add to variable lists
        speeds.append(stp.speed * 3.6)  # Must convert it to kph
        axis.append(stp.stepNum)
        inclination.append(stp.inclination * 10)
        soc.append(stp.battSoC)

    # Plot the data
    ax[0].cla()  # Clear axes
    ax[0].plot(axis, speeds, label='Speed')
    ax[0].plot(axis, soc, label='SoC')
    ax[0].plot(axis, inclination, label='Inclination')
    ax[0].set_title('GA Live Plot (Generation=' + str(generation) + ')')
    ax[0].set_xlabel('Distance / Km')
    ax[0].set_ylabel('Velocity / Kph')
    ax[0].legend()

    # Plot the histogram
    ax[1].cla()
    ax[1].hist(popFitnesses)
    ax[1].set_title('Race time histogram')
    ax[1].set_xlabel('Value')
    ax[1].set_ylabel('Frequency')

    # Pause to redraw the canvas
    plt.pause(0.01)

    # Print the race finish time:
    print "Race finish date and time: " + str(stp.gTime)