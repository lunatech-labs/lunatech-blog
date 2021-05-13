// Approach using Scala 3 Opaque Type Aliases

object Units {
  opaque type Kilometers = Double
  opaque type Miles = Double

  val ZeroKm: Kilometers = 0
  val ZeroMi: Miles = 0

  def kilometres(value: Double): Option[Kilometers] = if (value < 0) None else Some(value)
  def miles(value: Double): Option[Miles] = if (value < 0) None else Some(value)

  extension (km: Kilometers) {
    def + (km2: Kilometers): Kilometers = km + km2
  }

  extension (miles: Miles) {
    def toKilometers: Kilometers = miles * 1.6
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
    distance += booster.provideLaunchBoost().toKilometers
  }

  def distanceTravelled: Kilometers = distance
}

// For fun, let's make use of Scala 3's Univeral Apply Methods to omit the 'new'
val rocket: Rocket = Rocket(Booster())
rocket.launch();

// Will represent the correct distance travelled
rocket.distanceTravelled
