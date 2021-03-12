**Daily standup (9/2)**

Vi gick igenom projektet och vad som förväntades av oss för att fullfölja detta.
Sedan satte vi oss in i alla program såsom Jira för att skapa sprints.
Hade brainstorm för olika ideér och fastnade till slut i en motorcykel krasch sensor, som mäter
hojens lutning och om den hamnar under en viss vinkel och tid så skickas det ut ett sms till en 
ICE kontakt att personen har råkat ut för en olycka.
I denna diskussionen så har vi tankar på att skapa en applikation med hjälp av en raspberry pi samt
tillhörande hårdvara så som sensorer m.m. Vi plockar ihop en lösning på Electrokit.se som kan tänkas passa.

**Daily standup (11/2)**

Johan skapade olika sprints på Jira för att struktera upp vårt arbete, vi gemensamt kom 
med input om förväntad tid och resurser för att kunna producera vårt projekt och kom här fram till att
vi ville fokusera på mjukvaran och släpper därmed tankarna om att skapa en applikation med hårdvara.
Detta är dock något vi vill utveckla vidare i framtiden.
Undersökte en del om Cumulocity för att använda sensorerna i våra mobiler, frågan ställdes om vi 
kunde få ut datan från Cumulocity via mqtt. Denna frågan skulle Johan ta vidare till deras 
support.

**Daily standup (12/2)**

Vi löste vår MQTT publish/subscribe ihop med AWS IOT. 
Vi vill använda oss av accelerometer, gyro och location.
För att koppla samman så har vi valt att gå med Twilio SMS där vi sänder ett sms till våra enheter.
Vi avvaktar fortfarande svar från Cumulocity.
Inför nästa standup så skall vi börja kika på en inloggningssida.

**Daily standup (13/2)**

Vi behövde en inloggningssida där man loggar in med sin deviceID och lösenord. Detta löste Jessica
så vi har en fungerande inlogg som sedan leder oss till dashboard.


**Daily standup (14/2)**

Johan och Andreas inser att Cumulocity gyro sensor funkar ej som önskat (för långsam) så vi behöver hitta ett 
alternativ som är bättre. Nästa steg är att hitta en annan lösning och sammankoppla detta med vår applikation.
Jessica hittade en Android emulator där vi kan koppla oss till androids sensorer och därmed få ut all
nödvändig data. Detta skall vi undersöka inför nästa standup.
Jesper tittar på ett alternativ på en app som heter SDK Controller Sensor, en app som fungerar på Android och
som fungerar på samma sätt som Android emulator.

**Daily standup (15/2)**

Johan fick svar från Cumulocity att datan gick att få från cumulocity via rest-api så vi valde att gå med denna lösningen för att framkalla en krasch.
Vi valde att gå med cumulocity för att få ut location och istället node-red för att simulera en krasch och därefter skicka notis.
Detta för att fokusera på  övergripande syftet med projektet att koppla ihop med AWS.
Skapar en registreringssida för ny användare som ger access till dashboard.
Johan skall skapa en testdatabas för inlogg.

**Daily standup (16/2)**

Johan har skapat en sqlite-databas med exempeldata för användare/kontakter, detta för att vi skall kunna testa inloggning med deviceID.
Jessica jobbar vidare med dashboard.

**Daily standup (17/2)**

Fixa en dashboard med kontakter och min sida.
Lösa Node-Red för simulering av krasch som kopplar sig med mqtt.
Johan har lagt till två nya tabeller i databasen, ena tabellen för att spara cumulocity-uppgifter/användare och andra för gps-logg/användare
så att vi ska kunna utföra beräkningar som fordonets hastighet.

**Daily standup (19/2)**

Jesper jobbar med twilio för att få till att skicka sms, han skapar ett smsAPI för att kunna skicka ut
SMS kopplat med MQTT.


**Daily standup (24/2)**

Andreas fixar Node-red och kopplar ihop med MQTT.
Jessica fortsätter med dashboard.
Johan har modifierat registreringsidan så att man där tillfälligt kan ange sina cumulocity-uppgifter som krävs 
för gps-spårningen. Vi skall även skapa en sida där man kan lägga till och ta bort nödkontakter och ska ingå i dashboard.

**Daily standup (27/2)**

Andreas och Johan fixat kopplingen med Cumulocity där vi nu kan ta emot GPS position från telefonen.

**Daily Standup (4/3)**

Johan har löst login sessions så man inte behöver logga in varje gång.
Det sista på dashboard behöver lösas samt registreringsidan.

**Daily Standup (5/3)**

Vi har skapat en bakgrundstråd som hämtar GPS positionen kontinuerligt.
Johan har skapat en sida för tillägg och borttagning av nödkontakter som ingår i dashboarden.

**Daily Standup (7/3)**

Vi har lite kvar med sms funktionen vid simulerad krasch som vi ska lösa till nästa standup.

**Daily Standup (8/3)**

Andreas har nu löst så att det går att skicka sms till en enhet vid krasch, så nu får vi ett sms 
med förarens position. Detta styrs idag med hjälp av Node-Red.

**Daily Standup (10/3)**

Dashboard är klar med länkning av sidor så vi kan dema.
Då vi vill koppla upp oss till fler cloud tjänster så väljer vi att flytta från sqlite till MSSQL, detta då sqlite
funkar på en lokalnivå och vi vill ha även den i ett cloud.
Vi vill ha gearhost då vi vill undvika kostnader från AWS.

**Daily Standup (11/3)**

Johan har nu löst MSSQL och vi har testkört vår applikation för att eventuellt hitta buggar inför presentationen på fredag.

**Daily standup (12/3)**

Inlämning samt presentation av vår applikation inför klassen.
Därefter hade vi en intern återkoppling angående projektets slut.

