// Smart constructor approach that assumes Scala >= 2.13.2 and compiler flag -Xsource:3

import $scalac.`-Xsource:3`

object Units {
  sealed trait Distance extends Any
  final case class Kilometers private[Units] (value: Double) extends AnyVal with Distance
  final case class Miles private[Units] (value: Double) extends AnyVal with Distance

  val ZeroKm: Kilometers = Kilometers(0)
  val ZeroMi: Miles = Miles(0)

  def kilometers(value: Double): Option[Kilometers] = if (value < 0) None else Some(Kilometers(value))
  def miles(value: Double): Option[Miles] = if (value < 0) None else Some(Miles(value))

  def add(km1: Kilometers, km2: Kilometers): Kilometers = Kilometers(km1.value + km2.value)
  def toKilometers(distance: Distance): Kilometers = distance match {
    case miles: Miles => Kilometers(miles.value * 1.6)
    case kilometers: Kilometers => kilometers
  }
}

import Units._

class Booster() {
  def provideLaunchBoost(): Miles = miles(100).getOrElse(ZeroMi)
}

class Rocket(booster: Booster) {
  private var distance: Kilometers = ZeroKm

  def launch(): Unit = {
    val launchBoost: Kilometers = toKilometers(booster.provideLaunchBoost()) // Allocation of Miles object
    distance = add(distance, launchBoost)
  }

  def distanceTravelled: Kilometers = distance
}

val rocket: Rocket = new Rocket(new Booster())
rocket.launch();

// Will represent the correct distance travelled
rocket.distanceTravelled
