```mermaid
graph TD
    %% --- Level 0: Stakeholders (Root Causes) ---
    NHB["Number of NHB Heritage Site Designations"]
    URA["Number of URA Zoning Restrictions"]
    RelSites["Number of Religious Sites"]
    Edu["Capacity of Educational Institutions"]
    NEA["Number of NEA Mitigations"]

    %% --- Level 0.5: Infrastructure & Magnets ---
    Attractions["Density of Tourist Attractions"]
    Tourists["Volume of Tourists"]
    RelVisitors["Volume of Religious Attendees"]
    Students["Volume of Students"]
    Shops["Density of Commercial Shops"]

    %% --- Level 1: Environmental & Spatial Stressors ---
    Traffic["Volume of Vehicular Traffic"]
    Congestion["Level of Pedestrian Congestion"]
    AirPoll["Level of Air Pollution"]
    NoisePoll["Level of Noise Pollution"]
    Amenities["Degree of Amenity Accessibility"]

    %% --- Level 2: Human Impact (Health) ---
    Stress["Level of Psychological Stress"]
    Health["State of Physical Health"]
    Spirit["Strength of Community Spirit"]
    Events["Frequency of Community Events"]
    Complaints["Number of Resident Complaints"]

    %% --- Level 3: The Ultimate Output ---
    QoL["Resident Quality of Life"]
    Attractiveness["Level of Area Attractiveness"]

    %% --- Causal Links (The Pathways) ---

    %% The Generation Pathways
    NHB -->| + | Attractions
    Attractions -->| + | Tourists
    RelSites -->| + | RelVisitors
    Edu -->| + | Students
    
    %% The Congestion Bottleneck
    Tourists -->| + | Congestion
    Tourists -->| + | Traffic
    RelVisitors -->| + | Congestion
    Students -->| + | Congestion
    Students -->| + | Traffic
    Shops -->| + | Congestion
    Shops -->| + | Traffic

    %% Atomic Decomposition of QoL (The Core Logic)
    Congestion -->| - | Amenities
    Congestion -->| + | NoisePoll
    Traffic -->| + | AirPoll
    Traffic -->| + | NoisePoll

    NoisePoll -->| + | Stress
    Amenities -->| - | Stress
    AirPoll -->| - | Health
    Stress -->| - | Health

    Stress -->| - | QoL
    Health -->| + | QoL
    Spirit -->| + | QoL

    %% --- THE FEEDBACK LOOPS ---

    %% Loop R1 (Reinforcing): Community Erosion
    QoL -->| + | Events
    Events -->| + | Spirit
    %% R1 path: QoL -> Events -> Spirit -> QoL (0 negative links = R)

    %% Loop B1 (Balancing): Tourism Self-Correction
    Congestion -->| - | Attractiveness
    Attractiveness -->| + | Tourists
    %% B1 path: Tourists -> Congestion -> Attractiveness -> Tourists (1 negative link = B)

    %% Loop B2 (Balancing): URA Zoning Response & Delays
    QoL -->| - | Complaints
    Complaints -->| + | URA
    URA -.->| " - // delay " | Shops
    %% B2 path: QoL -> Complaints -> URA -> [delay] Shops -> Congestion -> Amenities -> Stress -> QoL (3 neg links = B)

    %% Loop B3 (Balancing): NEA Mitigation & Delays
    Complaints -->| + | NEA
    NEA -.->| " - // delay " | AirPoll
    NEA -.->| " - // delay " | NoisePoll
    %% B3 path: NEA mitigates pollution, restoring Health and QoL (odd negative links = B)
```

```plantuml
@startuml
skinparam defaultTextAlignment center
skinparam packageStyle rectangle
skinparam usecase {
    BackgroundColor White
    BorderColor Black
    ArrowColor Black
}

' --- Package Clustering for Layout Control ---

package "Policy & Governance" {
    (NHB Interventions) as NHB
    (Heritage Zoning Laws) as Zoning
    (NEA Interventions) as NEA
}

package "Heritage & Tourism Ecosystem" {
    (Level of Heritage Conservation) as Conservation
    (Density of Tourist Attractions) as Attractions
    (Overall Area Attractiveness) as Attractiveness
    (Volume of Tourists) as Tourists
}

package "Commercial, Civic & Educational" {
    (Number of Religious Sites) as RelSites
    (Volume of Religious Visitors) as RelVisitors
    (Frequency of Religious Events) as RelEvents
    (Number of Commercial Shops) as Shops
    (Number of Educational Institutions) as Edu
    (Student Population) as Students
}

package "Urban Environment" {
    (Level of Area Congestion) as Congestion
    (Traffic Volume) as Traffic
    (Level of Air Pollution) as AirPoll
    (Level of Noise Pollution) as NoisePoll
    (Amount of Green Space) as Greenery
    (Accessibility of Amenities) as Amenities
}

package "Resident Well-Being & Culture" {
    (Resident's Quality of Life) as QoL
    (Resident Complaints) as Complaints
    (Sense of Identity & Belonging) as Identity
    (Frequency of Community Events) as CommEvents
    (Level of Psychological Stress) as Stress
    (Overall Physical Health) as Health
    (Availability of Entertainment) as Entertainment
    (Art and Cultural Spaces) as Art
    (Personal Well-being) as Wellbeing
    (Environmental Sustainability) as Sustainability
}

' --- Invisible Grid Formatting ---
"Policy & Governance" -[hidden]down-> "Heritage & Tourism Ecosystem"
"Heritage & Tourism Ecosystem" -[hidden]right-> "Commercial, Civic & Educational"
"Heritage & Tourism Ecosystem" -[hidden]down-> "Urban Environment"
"Urban Environment" -[hidden]down-> "Resident Well-Being & Culture"

' --- Causal Links with Polarities ---

' Heritage & Tourism
NHB -down-> Conservation : +
NHB -down-> Zoning : +
Zoning -down-> Attractions : -
Conservation -down-> Attractions : +
Conservation -down---> Identity : +
Attractions -down-> Attractiveness : +
Attractiveness -down-> Tourists : +
Tourists -down---> Congestion : +
Tourists -down---> NoisePoll : +
Tourists -right-> Shops : +

' Religious Sites & Commercial
RelSites -down-> Shops : +
RelSites -down-> RelEvents : +
RelEvents -down-> RelVisitors : +
RelVisitors -up-> RelEvents : +
RelVisitors -down---> Congestion : +
RelEvents -down---> NoisePoll : +

' Urban Density & Congestion
Edu -down-> Students : +
Students -down---> Congestion : +
Traffic -down-> Congestion : +
Shops -down-> Traffic : +
Shops -down---> Congestion : +

' Environment & Health
Congestion -down-> AirPoll : +
Congestion -down-> NoisePoll : +
Congestion -down-> Amenities : -
NEA -down---> Greenery : +

' Greenery Mitigations
Greenery -up-> NoisePoll : -
Greenery -right-> AirPoll : -
Greenery -down-> Stress : -

AirPoll -down-> Health : -
NoisePoll -down-> Stress : +
NoisePoll -down---> QoL : -
Stress -down-> Health : -
Health -down-> QoL : +
Health -right-> Wellbeing : +

' Quality of Life & Culture
Amenities -down-> QoL : +
Art -down-> Entertainment : +
CommEvents -right-> Entertainment : +
CommEvents -left-> Identity : +
Entertainment -down-> QoL : +
Identity -down-> QoL : +

QoL -down-> Sustainability : +

' --- The Feedback Loops ---

' Reinforcing Loop (R1): Community Engagement
QoL -up-> CommEvents : +
note right of QoL : R1: Community Engagement\nHigher QoL drives events,\nreinforcing identity and QoL.

' Balancing Loop (B1): Tourism Limits to growth
Congestion -up---> Attractiveness : -
note right of Attractiveness : B1: Tourism Limits\nCongestion reduces\nattractiveness & capping tourists.

' Balancing Loop (B2): Civic/Policy Action
QoL -up---> Complaints : -
Complaints -up---> NEA : +
Complaints -up---> NHB : +
note left of Complaints : B2: Civic Action\nLower QoL drives complaints,\ntriggering policy limits.

@enduml