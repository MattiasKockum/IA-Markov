#!/usr/bin/env python3

"""
Program written by Mattias Kockum
On the 15/7/2020
The aime of this program is to create an AI capable of selective memory
"""

import numpy as np
import copy
import turtle
import matplotlib.pyplot as plt


def sigmoid(x):
	return(2*((1/(1+2.7**-(x)))-0.5))


class Problem():
    """
    The frame of any "live" problem
    """
    def __init__(self, warning = True):
        self.warning = warning
        self.nb_sensors = 1
        self.nb_actors = 1
        if self.warning:
            print("Warning  : __init__ was not fully configured") 

    def action(self, inputs):
        if self.warning:
            print("Warning  : action was not fully configured")
        pass

    def state(self):
        if self.warning:
            print("Warning  : action was not fully configured")
        return(np.array([1]))

    def experience(self, Chaîne):
        if self.warning:
            print("Warning  : experience was not fully configured")
        score = self.score_real_time()
        self.reset()
        return(score)

    def score_real_time(self):
        if self.warning:
            print("Warning score_real_time was not fully configured")
        return(0)

    def reset(self):
        self.__init__(self.warning)


class Herd():
    """
    Herd of networks that evolve by reproducing
    """
    def __init__(
        self,
        nb_sensors,
        nb_actors,
        nb_add_neurons,
        Problem,
        size = 30,
        mutation_coefficent = 0.001,
        nb_tests = 10,
        **kwargs
    ):
        self.size = size
        self.nb_sensors = nb_sensors
        self.nb_actors = nb_actors
        self.nb_add_neurons = nb_add_neurons
        self.mutation_coefficent = mutation_coefficent
        self.Problem = Problem
        self.members = [
            Network(nb_sensors, nb_actors, nb_add_neurons, **kwargs)
            for i in range(size)
        ]
        self.nb_tests = nb_tests
        self.array_scores = []

    def evolve(self, nb_iterations):
        """
        The idea is to make the AI evolve by aproximating the gradient descent
        """
        for iteration in range(nb_iterations):
            proba_reproduction = self.performances()
            new_members = [
                copy.deepcopy(
                    np.random.choice(
                    self.members,
                    p=proba_reproduction
                    )
                )
            for i in range(self.size)
            ]
            self.members = new_members
            for network in self.members:
                network.mutate(self.mutation_coefficent)
            self.array_scores.append(sum(self.score)/self.size)
        return(self.array_scores)

    def performances(self):
        """
        Evaluates performances then normalises them for probability operations
        """
        self.score = np.zeros(self.size)
        for i, j in enumerate(self.members):
            points = (
                sum([self.Problem.experience(j) for k in range(self.nb_tests)])
                /self.nb_tests
            )
            if points > 0:
                self.score[i] = points
            else:
                self.score[i] = 0
        if list(self.score) == list(np.zeros(self.size)):
            self.score = np.ones(self.size)
        score_modif = self.modif_score(self.score)
        return(score_modif)

    def modif_score(self, score):
        """
        Modifies the scores to make them useable in probability
        """
        return(score/sum(score))

    def scale(self, reproductive_members):
        """
        NOT USED YET
        scales up the members to make them able to reproduce
        """
        add_neurons = [0]*len(reproductive_members)
        nb_add_neurons = reproductive_members[0].nb_neurons
        for index, member in enumerate(reproductive_members[1:]):
            difference = member.nb_neurons - nb_add_neurons
            if difference > 0:
                nb_add_neurons = member.nb_neurons
                for i in range(index+1):
                    add_neurons[i] += difference
            else:
                add_neurons[index+1] -= difference
        for index, member in enumerate(reproductive_members):
            member.add_neurons(add_neurons[index])
        return(reproductive_members[0].nb_neurons)


class Network():
    """
    """
    def __init__(
        self,
        nb_sensors,
        nb_actors,
        nb_add_neurons,
        **kwargs # "weight", "bias", "slices", "regions"
    ):
        self.nb_sensors = nb_sensors
        self.nb_actors = nb_actors
        self.nb_add_neurons = nb_add_neurons
        self.nb_neurons = nb_add_neurons + nb_actors + nb_sensors
        self.values = np.zeros((self.nb_neurons))
        if ("slices" in kwargs and "regions" in kwargs):
            # slices = list of size of groups of deep neurons
            # regions = array of 0 and 1 if the group shall exist
            self.slices = [nb_sensors] + kwargs["slices"] + [nb_actors]
            self.regions = kwargs["regions"]
            self.squarred()
        elif "weight" not in kwargs and "bias" not in kwargs:
            self.random_set_up()
        elif (
            kwargs["weights"].shape == (nb_neurons, nb_neurons)
            and kwargs["bias"].shape == (nb_neurons,)
        ):
            self.weights = kwargs["weights"]
            self.bias = kwargs["bias"]
        else :
            raise(ValueError("Input matrices do not have the right format\
                             or both weights and bias or both slices and \
                             regions must be entered"))

    def random_set_up(self):
        self.weights = (
            np.random.rand(self.nb_neurons, self.nb_neurons)
            - 0.5
        )
        self.bias = np.random.rand(self.nb_neurons) - 0.5

    def squarred(self):
        self.directive = [[0]*len(self.slices)]*len(self.slices)
        self.slices_sum = [0]
        for i in self.slices:
            self.slices_sum.append(self.slices_sum[-1] + i)
        self.weights = np.zeros((self.nb_neurons, self.nb_neurons))
        l = len(self.slices)
        for indice_i, i in enumerate(range(l)):
            for indice_j, j in enumerate(range(l)):
                self.weights[
                    self.slices_sum[i]:self.slices_sum[i + 1],
                    self.slices_sum[j]:self.slices_sum[j + 1]
                ] = (
                    self.regions[i][j]
                    * (
                        np.random.rand(
                            self.slices[indice_i],
                            self.slices[indice_j]
                        )
                        - 0.5
                        )
                    )
        self.bias = np.random.rand(self.nb_neurons) - 0.5

    def __repr__(self):
        return("neurons : {}\n".format(self.nb_neurons)
               + "sensors : {}\n".format(self.nb_sensors)
               + "actors : {}\n".format(self.nb_actors)
               + "weights :\n{}\n".format(self.weights)
               + "bias :\n{}\n".format(self.bias)
               + "values :\n{}\n".format(self.values))

    def display(self):
        """
        Represents the network with
        """
        fig, ax = plt.subplots()
        array = np.concatenate((
            np.array([self.values]),
            np.array([self.bias]),
            self.weights
        ))
        im = ax.imshow(array)
        ax.set_yticks(np.arange(self.nb_neurons + 2))
        ax.set_yticklabels(["values"] + ["bias"] + ["weight"]*self.nb_neurons)
        ax.set_xticks(np.arange(self.nb_neurons))
        ax.set_xticklabels(
            ["sensor"]*self.nb_sensors
            + ["deep neuron"]*self.nb_add_neurons
            + ["actor"]*self.nb_actors
        )
        plt.setp(
            ax.get_xticklabels(),
            rotation=45,
            ha="right",
            rotation_mode="anchor"
        )
        ax.set_title("values of internal values, weights and bias")
        fig.tight_layout()
        plt.show()

    def input(self, values_inputs):
        self.values[:self.nb_sensors] += values_inputs

    def sortie(self):
        return(self.values[-self.nb_actors:])

    def iteration(self):
        """
        We iterate once and update network state
        """
        self.values = sigmoid(
            np.matmul(self.weights, self.values)
            + self.bias)

    def action(self, input):
        """
        What the network does over one iteration
        """
        self.input(input)
        self.iteration()
        return(self.sortie())

    def add_neurons(self, add_neurons=1):
        """
        NOT USED YET
        """
        # Creates bigger weights and bias arrays
        new_weights = np.zeros((self.weights.shape[0] + add_neurons,
                                   self.weights.shape[1] + add_neurons))
        new_bias = np.zeros((self.bias.shape[0] + add_neurons, ))
        nouvelles_values = np.zeros(self.nb_neurons + add_neurons)
        # Adds old values
        new_weights[:self.nb_sensors, :self.nb_sensors] = (
            self.weights[:self.nb_sensors, :self.nb_sensors])
        new_weights[-self.nb_sensors-1:, :self.nb_sensors] = (
            self.weights[-self.nb_sensors-1:, :self.nb_sensors])
        new_weights[-self.nb_sensors-1:, -self.nb_sensors-1:] = (
            self.weights[-self.nb_sensors-1:, -self.nb_sensors-1:])
        new_weights[:self.nb_sensors, -self.nb_sensors-1:] = (
            self.weights[:self.nb_sensors, -self.nb_sensors-1:])
        new_bias[:self.nb_sensors] = (
            self.bias[:self.nb_sensors])
        new_bias[-self.nb_sensors-1:] = (
            self.bias[-self.nb_sensors-1:])
        nouvelles_values[:self.nb_sensors] = (
            self.values[:self.nb_sensors])
        nouvelles_values[-self.nb_sensors-1:] = (
            self.values[-self.nb_sensors-1:])
        # Updates the network
        self.weights = new_weights
        self.bias = new_bias
        self.values = nouvelles_values
        self.nb_neurons += add_neurons
        # Returns the new number of nerons
        return(self.nb_neurons)

    def mutate(self, mutation_coefficent):
        """
        We mutate the Network
        """
        more_neurons = 0
        for i in range(self.nb_neurons*(self.nb_neurons + 1) + 1):
            # If there is a mutation
            if np.random.choice(
                [True, False],
                p = [mutation_coefficent, 1 - mutation_coefficent]
            ):
                # If the iterator corresponds to a weight, we modify it
                if i < self.nb_neurons**2:
                    self.weights[i//self.nb_neurons][i%self.nb_neurons] = (
                        np.random.rand() - 0.5
                    )
                # Elsif it corresponds to a bias we modify it
                elif i < self.nb_neurons*(self.nb_neurons + 1):
                    self.bias[i - self.nb_neurons**2] = (
                        np.random.rand() - 0.5
                    )
                # Else we add a neuron (NOT IMPLEMENTED YET)
                else:
                    more_neurons += 1
            pass

class TestBench():
    """
    A test bench to verify everything works fine
    """

    def __init__(
        self,
        problem,
        nb_herds = 20,
        nb_generations = 20,
        nb_add_neurons = 9,
        size = 30,
        mutation_coefficent = 0.02,
        nb_tests = 5,
        **kwargs
    ):
        self.kwargs = kwargs
        if "slices" in kwargs:
            self.nb_add_neurons = sum(kwargs["slices"])
        else:
            self.nb_add_neurons = nb_add_neurons
        self.series = []
        self.problem = problem
        self.nb_sensors = problem.nb_sensors
        self.nb_actors = problem.nb_actors
        self.colors = ["r", "g", "b", "c", "m", "y", "k"]
        self.nb_herds = nb_herds
        self.nb_generations = nb_generations
        self.size = size
        self.mutation_coefficent = mutation_coefficent
        self.nb_tests = nb_tests
        self.values_simple = self.nb_herds*[1]
        self.values_nb_add_neurons = [0, 1, 2, 3, 4, 5, 6]
        self.values_sizes = [2, 5, 10, 15, 20, 30]
        self.values_mutation_coefficients = [0.01, 0.005, 0.002, 0.001]
        self.values_nb_tests = [1, 2, 3, 4, 5, 6]
        self.archives = []

    def represent(self):
        for indice, serie in enumerate(self.series):
            plt.plot(
                [k for k in range(len(serie))],
                serie,
                self.colors[indice%len(self.colors)]+"-*"
            )
        plt.show()

    def test(self, mode = 0, nb_generations = None, values = None):
        if nb_generations == None:
            nb_generations = self.nb_generations
        base = [
            self.nb_sensors,
            self.nb_actors,
            self.nb_add_neurons,
            self.problem,
            self.size,
            self.mutation_coefficent,
            self.nb_tests
        ]
        if mode in [0, "simple"]:
            if values == None:
                values = self.values_simple
            array_inputs = np.array([base for i in range(len(values))])
        if mode in [1, "nb_neurons"]:
            if values == None:
                values = self.values_nb_add_neurons
            array_inputs = np.array([base for i in range(len(values))])
            array_inputs[:,2] = values
        if mode in [2, "size"]:
            if values == None:
                values = self.values_sizes
            array_inputs = np.array([base for i in range(len(values))])
            array_inputs[:,4] = values
        if mode in [3, "coefficient_mutation"]:
            if values == None:
                values = self.values_mutation_coefficients
            array_inputs = np.array([base for i in range(len(values))])
            array_inputs[:,5] = values
        if mode in [4, "nb_tests"]:
            if values == None:
                values = self.values_nb_tests
            array_inputs = np.array([base for i in range(len(values))])
            array_inputs[:,6] = values
        if mode in [5, "multiple"]:
            if values == None:
                raise(ValueError("An array must be in input"))
            array_inputs = np.array([base for i in range(len(values))])
            array_inputs = values
        print(
            "\n",
            "(1) nb_captors\n",
            "(2) nb_actors\n",
            "(3) nb_add_neurons\n",
            "(4) Problem\n",
            "(5) herd's size\n",
            "(6) mutation_coefficent\n",
            "(7) colors\n",
            "\n",
            "(1)(2)(3)(4)(5)(6)(7)"
        )
        for i in range(len(values)):
            print(*array_inputs[i], self.colors[i%len(self.colors)])
            T = Herd(*array_inputs[i], **self.kwargs)
            self.series.append(T.evolve(nb_generations))
            self.archives.append([T.members[0], self.series])
        self.represent()
        self.series = []


print(
"""
P = Car(False)
TB = TestBench(P, slices=[5, 4], regions=[[False, True, False, False], [False,
    False, True, False], [False, False, False, True], [False, False, False,
    False]])

TB.test(0)
"""
)