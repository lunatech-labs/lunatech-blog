// Smart constructor approach that assumes Scala >= 2.13.2 and compiler flag -Xsource:3

import $scalac.`-Xsource:3`

object Units {
  sealed trait Distance extends Any
  final case class Kilometres private[Units] (value: Double) extends AnyVal with Distance
  final case class Miles private[Units] (value: Double) extends AnyVal with Distance

  val ZeroKm: Kilometres = Kilometres(0)
  val ZeroMi: Miles = Miles(0)

  def kilometres(value: Double): Option[Kilometres] = if (value < 0) None else Some(Kilometres(value))
  def miles(value: Double): Option[Miles] = if (value < 0) None else Some(Miles(value))

  def add(km1: Kilometres, km2: Kilometres): Kilometres = Kilometres(km1.value + km2.value)
  def toKm(distance: Distance): Kilometres = distance match {
    case miles: Miles => Kilometres(miles.value * 1.6)
    case kilometres: Kilometres => kilometres
  }
}

import Units._

class Booster() {
  def provideLaunchBoost(): Miles = miles(100).getOrElse(ZeroMi)
}

class Rocket(booster: Booster) {
  private var distance: Kilometres = ZeroKm

  def launch(): Unit = {
    val launchBoost: Kilometres = toKm(booster.provideLaunchBoost()) // Allocation of Miles object
    distance = add(distance, launchBoost)
  }

  def distanceTravelled: Kilometres = distance
}

val rocket: Rocket = new Rocket(new Booster())
rocket.launch();

// Will represent the correct distance travelled
rocket.distanceTravelled
