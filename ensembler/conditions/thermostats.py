from ensembler.system.basic_system import system as sys
from ensembler.conditions._conditions import Condition

import warnings
import numpy as np
from scipy import constants as const
from scipy.stats import boltzmann, maxwell

class thermostat(Condition):
    """
    ..autoclass: Thermostat
        This is the parent class of Thermostats.
        The apply function of this class is not implemented and needs to be overwritten by each subclass.
    """

    _currentTemperature:float
    system:sys #system
    verbose:bool = False

    def __init__(self, system:sys, tau:float, ):
        self.system = system
        self.tau = tau

class andersonThermostat(thermostat):
    """ -UnderConstuction-
    andersenThermostat 
        This thermostat was developed by anderson 1980 and is also called stochastic collisions method.
        This method is optimal for single particle simulations as it tries to simulate a particle that collides with virtual particles from  a temperature bath.
        At each collision, the velocity and the interval of the next collision is randomly reassigned and reselected from a Maxwell-Boltzmann distribution.
        This applying the thermostat leads to an at least microcanonical Simulation. Simulated energies should be gaussian distributed.

        [Molecular Modelling Principles and Applications, A. R. Leach, second edition]
        FIX MAXWWELL POSITIONING!
    """

    #collision parameters
    kb:float = const.k*const.Avogadro
    a:float = 1 #dimensionless constant
    k:float = 1 #thermal konductivity
    N_dens:float = 0.1 #particle density
    N:float =10 #particle

    #temperaturebath:
    temperature:float   #desired temperature area
    temperature_noise_range:float 
    _new_temperature:float
    _lambda:float =1  #scaling factor for velocities

    """Under COnstructurion"""
    def __init__(self, temperature:float=298, temperature_noise_range:float=25, MConstraintsDims:int=1, system:sys=None,
                    kb=const.k*const.Avogadro, a:float = 1, k:float=1, N_dens:float=0.005, N:float=1, verbose:bool=False ):
        warnings.warn("__Under construction___!")
        #Collision parameters
        self.kb = kb
        self.a = a #dimensionless constant
        self.k = k #thermal konductivity
        self.N_dens = N_dens #particle density
        self.N =N #particle

        #Temperature Scalingparameters
        self.temperature_noise_range = temperature_noise_range
        
        self.M = MConstraintsDims


        if(system != None):
            self.system = system
            self.temperature = self.system.temperature
        else:
            self.temperature = temperature

        self.verbose = verbose

    def _collision(self)->bool:
        p_collision = (2*self.a*self.k)/(3*self.kb*self.N_dens**(1/3)*self.N**(2/3))
        options = [True, False]
        collision = np.random.choice(a=options, p=(p_collision, 1-p_collision))
        return collision

    def _rescale_velocities(self):
        orig_vels = self.system._currentVelocities
        new_vels = self._lambda * orig_vels if(self._lambda * orig_vels) else 0.0001    #do not allow 0 vel
        self.system._currentVelocities = new_vels

    def _calculate_scaling_factor(self):
        #pick new temperature randomly
        self._new_temperature = maxwell.rvs(loc=self.temperature-self.temperature_noise_range, scale=self.temperature_noise_range)
        self._currentTemperature = (self.system._currentTemperature if (self.system._currentTemperature!=0) else 0.000001)
        self.system._currentTemperature = self._new_temperature
        #scaling factor
        self._lambda = self._new_temperature/self._currentTemperature  #(1+(self.dt/self.tau)*((self.system.temperature/T_t)-1))**0.5


    def apply(self):
        if(self._collision()):
            self._calculate_scaling_factor()
            self._rescale_velocities()

            if(self.verbose):
                print("THERMOSTAT: get to temp: ", self.system._currentTemperature,"\n"
                        'THERMOSTAT: tot_kin: ', self.system.totKin(),"\n"
                        "THERMOSTAT: lambda: ", self._lambda,"\n"
                        "THERMOSTAT: current_Velocity: ", self.system._currentVelocities, "\n"
                        "\n")
        else:
            pass

class berendsenThermostate(thermostat):
    """
    ..autoclass: berendsen Thermostat

        reference: Molecular dynamics with coupling to an external bath; H.J.C. Berendsen
    """

    def __init__(self, tau:float, dt:float, MConstraintsDims:int=1, system:sys=None ):
        self._lambda:float=1   #scaling factor of velocities
        self._current_temperatur = 1
        self.tau = tau
        self.dt = dt
        self.M = MConstraintsDims

        if(system != None):
            self.system = system

    def apply(self):
        self._calculate_current_temperature()
        self._calculate_scaling_factor()
        self._rescale_velocities()
        
        if(self.verbose):
            print("THERMOSTAT: get to temp: ", self.system.temperature,"\n"
                  'THERMOSTAT: tot_kin: ', self.system.totKin(),"\n"
                  "THERMOSTAT: curr temp: ", self._current_temperatur,"\n"
                  "THERMOSTAT: lambda: ", self._lambda,"\n"
                  "THERMOSTAT: current_Velocity: ", self.system._currentVelocities, "\n"
                  "\n")

    def _rescale_velocities(self):
        orig_vels = self.system._currentVelocities
        new_vels = abs(self._lambda) * orig_vels if(self._lambda * orig_vels) else 0.0001    #do not allow 0 vel
        self.system._currentVelocities = new_vels

    def _calculate_current_temperature(self):
        """
        autofunction: _calculate current Temperature (eq. 32,33)
        :return:
        """
        #M = constraints
        N=self.system.nparticles * const.Avogadro
        self._current_temperatur = (2/(3*N-self.M-3))*self.system.totKin()*N
        self.system._currentTemperature = self._current_temperatur

    def _calculate_scaling_factor(self):
        """
        autofunction: _calculate_scaling_factor
            (eq.34)
        :return:
        """
        T_t = (self._current_temperatur if (self._current_temperatur!=0) else 0.000001)
        self._lambda = (1+(self.dt/self.tau)*((self.system.temperature/T_t)-1))**0.5



"""
class nhIntegrator(integrator): Nosehover-leapfrog
    def scaleVel(self, sys):
        freetemp = 2.0 / const.gas_constant / 1000.0 * sys.mu * sys.new_velocity ** 2  # t+0.5Dt
        self.oldxi = self.xi  # t-0.5Dt
        self.xi += self.dt / (self.tau * self.tau) * (freetemp / sys.temp - 1.0)  # t+0.5t
        scale = 1.0 - self.xi * self.dt
        return scale

    def step(self, sys):
        sys.pos = sys.newpos  # t
        sys.force = -sys.pot.dhdpos(sys.lam, sys.pos)  # t
        sys.oldvel = sys.new_velocity  # t - 0.5 Dt
        sys.new_velocity += sys.force / sys.mu * self.dt  # t+0.5t
        sys.new_velocity *= self.scaleVel(sys)
        sys.vel = 0.5 * (sys.oldvel + sys.new_velocity)
        sys.newpos += self.dt * sys.new_velocity  # t+Dt
        sys.veltemp = sys.mu / const.gas_constant/1000.0 * sys.vel ** 2  # t
        sys.updateEne()
        return [sys.pos, sys.vel, sys.veltemp, sys.totkin, sys.totpot, sys.totene, sys.lam, sys.dhdlam]

    def __init__(self, xi=0.0, tau=0.1, dt=1e-1):
        self.xi = xi
        self.oldxi = xi
        self.tau = tau
        self.dt = dt
        raise NotImplementedError("This "+__class__+" class is not implemented")

class hmcIntegrator(integrator):
    def step(self, sys):
        accept = 0
        oldene = sys.totene
        oldpos = sys.pos  # t
        oldvel = sys.vel
        sys.initVel()  # t-0.5Dt
        for i in range(self.steps):
            sys.pos += self.dt * sys.new_velocity  # t
            force = -sys.pot.dhdpos(sys.lam, sys.pos)  # t
            sys.vel = (oldvel + sys.new_velocity) / 2.0
            sys.veltemp = sys.mu / const.gas_constant / 1000.0 * sys.vel ** 2  # t
            sys.updateEne()
            oldvel = sys.new_velocity
            sys.new_velocity += force / sys.mu * self.dt  # t+0.5t
        accept = 0
        if sys.totene < oldene:
            accept = 1
        else:
            if np.random.rand() <= np.exp(-1 / (const.gas_constant / 1000.0* sys.temp) * (sys.totene - oldene)):
                accept = 1
        if accept == 0:
            sys.pos = oldpos
            sys.vel = oldvel
            sys.veltemp = sys.mu / const.gas_constant * sys.vel ** 2  # t
            sys.updateEne()
        return [sys.pos, sys.vel, sys.veltemp, sys.totkin, sys.totpot, sys.totene, sys.lam, sys.dhdlam]

    def __init__(self, steps=5, dt=1e-1):
        self.steps = steps
        self.dt = dt
        raise NotImplementedError("This "+__class__+" class is not implemented")

"""