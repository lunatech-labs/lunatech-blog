// Approach using Scala 3 Opaque Type Aliases

object Units {
  opaque type Kilometres = Double
  opaque type Miles = Double

  val ZeroKm: Kilometres = 0
  val ZeroMi: Miles = 0

  def kilometres(value: Double): Option[Kilometres] = if (value < 0) None else Some(value)
  def miles(value: Double): Option[Miles] = if (value < 0) None else Some(value)

  extension (km: Kilometres) {
    def + (km2: Kilometres): Kilometres = km + km2
  }

  extension (miles: Miles) {
    def toKm: Kilometres = miles * 1.6
  }
}

import Units._

class Booster() {
  def provideLaunchBoost(): Miles = miles(100).getOrElse(ZeroMi)
}

class Rocket(booster: Booster) {
  private var distance: Kilometres = ZeroKm

  def launch(): Unit = {
    // Kilometres and Miles are different types. So compiler prevents the previous bug
    distance += booster.provideLaunchBoost().toKm
  }

  def distanceTravelled: Kilometres = distance
}

// For fun, let's make use of Scala 3's Univeral Apply Methods to omit the 'new'
val rocket: Rocket = Rocket(Booster())
rocket.launch();

// Will represent the correct distance travelled
rocket.distanceTravelled
