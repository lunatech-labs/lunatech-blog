// Smart constructor approach that assumes Scala >= 2.13.2 and compiler flag -Xsource:3

import $scalac.`-Xsource:3`

object Units {
  final case class Kilometers private[Units] (value: Double) extends AnyVal
  final case class Miles private[Units] (value: Double) extends AnyVal

  val ZeroKm: Kilometers = Kilometers(0)
  val ZeroMi: Miles = Miles(0)

  def kilometers(value: Double): Option[Kilometers] = if (value < 0) None else Some(Kilometers(value))
  def miles(value: Double): Option[Miles] = if (value < 0) None else Some(Miles(value))

  def add(km1: Kilometers, km2: Kilometers): Kilometers = Kilometers(km1.value + km2.value)
  def toKilometers(miles: Miles): Kilometers = Kilometers(miles.value * 1.6)
}

import Units._

class Booster() {
  def provideLaunchBoost(): Miles = miles(100).getOrElse(ZeroMi)
}

class Rocket(booster: Booster) {
  private var distance: Kilometers = ZeroKm

  def launch(): Unit = {
    // Kilometers and Miles are different types. So compiler prevents the previous bug
    val launchBoost: Kilometers = toKilometers(booster.provideLaunchBoost())
    distance = add(distance, launchBoost)
  }

  def distanceTravelled: Kilometers = distance
}

val rocket: Rocket = new Rocket(new Booster())
rocket.launch();

// Will represent the correct distance travelled
rocket.distanceTravelled
