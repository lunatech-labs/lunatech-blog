// Approach using Scala 3 Opaque Type Aliases

object Units {
  opaque type Kilometers = Double
  opaque type Miles = Double

  val ZeroKm: Kilometers = 0
  val ZeroMi: Miles = 0

  def kilometers(value: Double): Option[Kilometers] = if (value < 0) None else Some(value)
  def miles(value: Double): Option[Miles] = if (value < 0) None else Some(value)

  def add(km1: Kilometers, km2: Kilometers): Kilometers = km1 + km2
  def toKilometers(miles: Miles): Kilometers = miles * 1.6

  extension (km: Kilometers) {
    def + (km2: Kilometers): Kilometers = add(km, km2)
  }

  extension (miles: Miles) {
    def toKm: Kilometers = toKilometers(miles)
  }
}

import Units._

class Booster() {
  def provideLaunchBoost(): Miles = miles(100).getOrElse(ZeroMi)
}

class Rocket(booster: Booster) {
  private var distance: Kilometers = ZeroKm

  def launch(): Unit = {
    // Kilometers and Miles are different types. So compiler prevents the previous bug
    distance += booster.provideLaunchBoost().toKm
  }

  def distanceTravelled: Kilometers = distance
}

// For fun, let's make use of Scala 3's Universal Apply Methods to omit the 'new'
val rocket: Rocket = Rocket(Booster())
rocket.launch();

// Will represent the correct distance travelled
rocket.distanceTravelled
