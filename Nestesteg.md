Det neste blir å:
 ----- * Opprette filer på client siden som skal sendes
 ----- * Sende filer til server, i tidsrommet (sende inn tidsrommet i handleclient)
 ----- * Når tiden er ute, sende en Bye melding
 

 ----- * Ta imot pakker på server siden
 ----- * Telle antall pakker/Mbps/MB
 ----- * Sende en ACK bye når man har mottat bye. 

 ----- * utskrift på clientside med hvor mye som har blitt sendt
 ----- * faktisk hente inn og bruke tiden som blir satt
 * kode de andre flaggene (å sende på antall pakker isteden for tid, parallell osv...)
 ----- * Lage kode for å skrive ut hver x sekund på client siden
 ----- * Kode check_format?

 * Hvordan lage forskjell mellom når man kjører threadserver og vanlig server. 
    * Den forskjellen skal skje når man kjører server, ikke client, det er noe eget. 

        Må lage noe som tilsier at man kjører thread på server, kodene for det server thread er laget.
        Må lage en kode på client siden som lager antall connecions/cleints som det tallet som ble sendt inn. Og som derretter prøver å koble seg til. Er det bare å lage en forløkke som sender inn connections? Eller venter til en connection er ferdig da?

        Må jeg sende alle pakkene fra client, før jeg kan starte opp connection nr 2? Hvordan blir det på client siden?

* Endre fra bytes til bit. OBS! Pass på at du får ca 4000 mpbs når du kjører alle de forskjellige argumentene
* Endre fra bye == til bye in message 

