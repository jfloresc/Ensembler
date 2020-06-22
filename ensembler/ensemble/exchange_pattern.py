import numpy as np
from ensembler.ensemble import _replica_graph

class Exchange_pattern:
    replica_graph=None

    def __init__(self, replica_graph):
        self.replica_graph = replica_graph

    def exchange(self, verbose:bool=False):
        raise NotImplementedError("Not Implemented")

    def _do_exchange(self, exchanges_to_make, verbose:bool=False):

        for (I, J), exchange in exchanges_to_make.items():
            if(exchange):
                if (verbose): print("Exchanging: " + str(I) + "\t" + str(J) + "\t" + str(exchange) + "\n")

                partnerI = self.replica_graph.replicas[I]
                partnerJ = self.replica_graph.replicas[J]

                #here the real exchange happens!
                tmp_exchange_parameter = getattr(partnerI, self.replica_graph.exchange_param)
                setattr(partnerI, self.replica_graph.exchange_param, getattr(partnerJ, self.replica_graph.exchange_param))
                setattr(partnerJ, self.replica_graph.exchange_param, tmp_exchange_parameter)

                #here we follow the exchanges with the replicaID
                tmp_id = getattr(partnerI, "replicaID")
                setattr(partnerI, "replicaID", getattr(partnerJ, "replicaID"))
                setattr(partnerJ, "replicaID", tmp_id)

                #This is traj specific.... - might overwrite other params
                if(self.replica_graph.exchange_param == "trajectory"):
                    partnerI._update_state_from_traj()
            else:
                if (verbose): print("not Exchanging: " + str(I) + " / " + str(J) + " \n")

    def update_exchange_information(self, original_exchange_coordinates, original_totPots, swapped_totPots):
        if (self.exchange_offset == 1):
            exchange = False
            IJ = original_exchange_coordinates[0]
            replicaIJ = self.replica_graph.replicas[IJ]
            self.replica_graph.exchange_information = self.replica_graph.exchange_information.append(
                {"nExchange": self.replica_graph._currentTrial, "replicaID": replicaIJ.replicaID,
                 "replicaPositionI": IJ, "exchangeCoordinateI": replicaIJ.exchange_parameters, "TotEI": swapped_totPots[IJ],
                 "replicaPositionJ": IJ, "exchangeCoordinateJ": replicaIJ.exchange_parameters, "TotEJ": swapped_totPots[IJ],
                 "doExchange": exchange}, ignore_index=True)
            
        for (I, J), exchange in self.replica_graph._current_exchanges.items():     
            replicaI = self.replica_graph.replicas[I]
            replicaJ = self.replica_graph.replicas[J]
            # add exchange info line here!
            self.replica_graph.exchange_information = self.replica_graph.exchange_information.append(
                {"nExchange": self.replica_graph._currentTrial, "replicaID": replicaI.replicaID,
                    "replicaPositionI": I, "exchangeCoordinateI": replicaI.exchange_parameters, "TotEI": original_totPots[I],
                    "replicaPositionJ": J, "exchangeCoordinateJ": replicaJ.exchange_parameters, "TotEJ": original_totPots[J],
                    "doExchange": exchange}, ignore_index=True)
            self.replica_graph.exchange_information = self.replica_graph.exchange_information.append(
                {"nExchange": self.replica_graph._currentTrial, "replicaID": replicaJ.replicaID,
                    "replicaPositionI": J, "exchangeCoordinateI": replicaJ.exchange_parameters, "TotEI": swapped_totPots[J],
                    "replicaPositionJ": I, "exchangeCoordinateJ": replicaI.exchange_parameters, "TotEJ": swapped_totPots[I],
                    "doExchange": exchange}, ignore_index=True)

        if (self.exchange_offset == 0):
            exchange = False
            IJ = original_exchange_coordinates[-1]
            replicaIJ = self.replica_graph.replicas[IJ]
            self.replica_graph.exchange_information = self.replica_graph.exchange_information.append(
                {"nExchange": self.replica_graph._currentTrial, "replicaID": replicaIJ.replicaID,
                 "replicaPositionI": IJ, "exchangeCoordinateI": replicaIJ.exchange_parameters, "TotEI": swapped_totPots[IJ],
                 "replicaPositionJ": IJ, "exchangeCoordinateJ": replicaIJ.exchange_parameters, "TotEJ": swapped_totPots[IJ],
                 "doExchange": exchange}, ignore_index=True)




class localExchangeScheme(Exchange_pattern):

    exchange_offset:int=0

    def exchange(self, verbose:bool=False):
        """
        .. autofunction:: Exchange the Trajectory of T-replicas in pairwise fashion
        :param verbose:
        :return:
        """
        self.replica_graph._currentTrial += 1

        #Get Potential Energies
        original_exchange_coordinates, original_totPots, swapped_exchange_coordinates, swapped_totPots = self._collect_replica_energies(verbose)

        if(verbose):
            print("origTotE ", [original_totPots[key] for key in sorted(original_exchange_coordinates)])
            print("SWPTotE ", [swapped_totPots[key] for key in sorted(swapped_exchange_coordinates)])

        #decide exchange
        exchanges_to_make={}
        for partner1, partner2 in zip(original_exchange_coordinates[self.exchange_offset::2], original_exchange_coordinates[1+self.exchange_offset::2]):
            originalEnergies = np.add(original_totPots.get(partner1), original_totPots.get(partner2))
            swapEnergies = np.add(swapped_totPots.get(partner1), swapped_totPots.get(partner2))
            exchanges_to_make.update({(partner1, partner2): self.replica_graph.exchange_criterium(originalEnergies, swapEnergies)})

        #Acutal Exchange of params (actually trajs here
        if(verbose):
            print("Exchange: ", exchanges_to_make)
            print("exchaning param: ", self.replica_graph.exchange_param)

        #execute exchange
        self._do_exchange(exchanges_to_make=exchanges_to_make)

        #update exchange info
        self.replica_graph._current_exchanges = exchanges_to_make
        self.update_exchange_information(original_exchange_coordinates=original_exchange_coordinates, original_totPots=original_totPots, swapped_totPots=swapped_totPots)
        #update the offset
        self.exchange_offset = (self.exchange_offset+1)%2

    def _swap_coordinates(self, original_exCoord):
        ##take care of offset situations and border replicas
        swapped_exCoord = [] if self.exchange_offset == 0 else [original_exCoord[0]]
        ##generate sequence with swapped params
        for partner1, partner2 in zip(original_exCoord[self.exchange_offset::2],
                                        original_exCoord[1 + self.exchange_offset::2]):
            swapped_exCoord.extend([partner2, partner1])
        ##last replica on the border?
        if (self.exchange_offset == 0):
            swapped_exCoord.append(original_exCoord[-1])

        return swapped_exCoord

    ##Exchange functions
    def _collect_replica_energies(self, verbose=False):
        original_totPots = self.replica_graph.get_total_energy()
        original_exCoord = list(sorted(original_totPots.keys()))

        replica_values = list([self.replica_graph.replicas[key] for key in original_exCoord])

        # SWAP exchange_coordinates params pairwise
        swapped_exCoord = self._swap_coordinates(original_exCoord)

        if (verbose):
            print("original Coords ", original_exCoord)
            print("swapped Coords ", swapped_exCoord)

        # SWAP Params to calculate energies in swapped case
        self.replica_graph.set_parameter_set(coordinates=swapped_exCoord, replicas=replica_values)  # swap parameters

        # Exchange coordinate paramters:
        ##scaleVel
        self.replica_graph._adapt_system_to_exchange_coordinate(swapped_exCoord, original_exCoord)

        ##get_swapped energies
        swapped_totPots = self.replica_graph.get_total_energy()  # calc swapped parameter Energies

        ##scale Vel back
        self.replica_graph._adapt_system_to_exchange_coordinate(swapped_exCoord, original_exCoord)
        self.replica_graph.set_parameter_set(coordinates=original_exCoord, replicas=replica_values)  # swap back parameters

        return original_exCoord, original_totPots, swapped_exCoord, swapped_totPots

class globalExchangeScheme(Exchange_pattern):

    def exchange(self, verbose:bool=False):
        pass