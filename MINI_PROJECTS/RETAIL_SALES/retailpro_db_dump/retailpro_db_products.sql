-- MySQL dump 10.13  Distrib 8.0.36, for Win64 (x86_64)
--
-- Host: localhost    Database: retailpro_db
-- ------------------------------------------------------
-- Server version	8.0.36

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products` (
  `product_id` int NOT NULL,
  `product_name` varchar(100) NOT NULL,
  `category` varchar(50) NOT NULL,
  `subcategory` varchar(50) NOT NULL,
  `unit_cost` decimal(10,2) NOT NULL,
  `unit_price` decimal(10,2) NOT NULL,
  PRIMARY KEY (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES (1,'Wireless Mouse 001','Electronics','Accessories',300.00,495.00),(2,'Wireless Mouse 002','Electronics','Accessories',347.00,572.55),(3,'Wireless Mouse 003','Electronics','Accessories',394.00,650.10),(4,'Wireless Mouse 004','Electronics','Accessories',441.00,727.65),(5,'Wireless Mouse 005','Electronics','Accessories',488.00,805.20),(6,'Wireless Mouse 006','Electronics','Accessories',535.00,882.75),(7,'Wireless Mouse 007','Electronics','Accessories',582.00,960.30),(8,'Wireless Mouse 008','Electronics','Accessories',329.00,542.85),(9,'Wireless Mouse 009','Electronics','Accessories',376.00,620.40),(10,'Wireless Mouse 010','Electronics','Accessories',423.00,697.95),(11,'Wireless Mouse 011','Electronics','Accessories',470.00,775.50),(12,'Wireless Mouse 012','Electronics','Accessories',517.00,853.05),(13,'Wireless Mouse 013','Electronics','Accessories',564.00,930.60),(14,'Wireless Mouse 014','Electronics','Accessories',311.00,513.15),(15,'Wireless Mouse 015','Electronics','Accessories',358.00,590.70),(16,'Wireless Mouse 016','Electronics','Accessories',405.00,668.25),(17,'Wireless Mouse 017','Electronics','Accessories',452.00,745.80),(18,'Wireless Mouse 018','Electronics','Accessories',499.00,823.35),(19,'Wireless Mouse 019','Electronics','Accessories',546.00,900.90),(20,'Wireless Mouse 020','Electronics','Accessories',593.00,978.45),(21,'Keyboard 021','Electronics','Computer Accessories',960.00,1488.00),(22,'Keyboard 022','Electronics','Computer Accessories',533.00,826.15),(23,'Keyboard 023','Electronics','Computer Accessories',606.00,939.30),(24,'Keyboard 024','Electronics','Computer Accessories',679.00,1052.45),(25,'Keyboard 025','Electronics','Computer Accessories',752.00,1165.60),(26,'Keyboard 026','Electronics','Computer Accessories',825.00,1278.75),(27,'Keyboard 027','Electronics','Computer Accessories',898.00,1391.90),(28,'Keyboard 028','Electronics','Computer Accessories',971.00,1505.05),(29,'Keyboard 029','Electronics','Computer Accessories',544.00,843.20),(30,'Keyboard 030','Electronics','Computer Accessories',617.00,956.35),(31,'Keyboard 031','Electronics','Computer Accessories',690.00,1069.50),(32,'Keyboard 032','Electronics','Computer Accessories',763.00,1182.65),(33,'Keyboard 033','Electronics','Computer Accessories',836.00,1295.80),(34,'Keyboard 034','Electronics','Computer Accessories',909.00,1408.95),(35,'Keyboard 035','Electronics','Computer Accessories',982.00,1522.10),(36,'Keyboard 036','Electronics','Computer Accessories',555.00,860.25),(37,'Keyboard 037','Electronics','Computer Accessories',628.00,973.40),(38,'Keyboard 038','Electronics','Computer Accessories',701.00,1086.55),(39,'Keyboard 039','Electronics','Computer Accessories',774.00,1199.70),(40,'Keyboard 040','Electronics','Computer Accessories',847.00,1312.85),(41,'Office Chair 041','Furniture','Office Furniture',5240.00,7598.00),(42,'Office Chair 042','Furniture','Office Furniture',5371.00,7787.95),(43,'Office Chair 043','Furniture','Office Furniture',5502.00,7977.90),(44,'Office Chair 044','Furniture','Office Furniture',5633.00,8167.85),(45,'Office Chair 045','Furniture','Office Furniture',5764.00,8357.80),(46,'Office Chair 046','Furniture','Office Furniture',5895.00,8547.75),(47,'Office Chair 047','Furniture','Office Furniture',3026.00,4387.70),(48,'Office Chair 048','Furniture','Office Furniture',3157.00,4577.65),(49,'Office Chair 049','Furniture','Office Furniture',3288.00,4767.60),(50,'Office Chair 050','Furniture','Office Furniture',3419.00,4957.55),(51,'Office Chair 051','Furniture','Office Furniture',3550.00,5147.50),(52,'Office Chair 052','Furniture','Office Furniture',3681.00,5337.45),(53,'Office Chair 053','Furniture','Office Furniture',3812.00,5527.40),(54,'Office Chair 054','Furniture','Office Furniture',3943.00,5717.35),(55,'Office Chair 055','Furniture','Office Furniture',4074.00,5907.30),(56,'Office Chair 056','Furniture','Office Furniture',4205.00,6097.25),(57,'Office Chair 057','Furniture','Office Furniture',4336.00,6287.20),(58,'Office Chair 058','Furniture','Office Furniture',4467.00,6477.15),(59,'Office Chair 059','Furniture','Office Furniture',4598.00,6667.10),(60,'Office Chair 060','Furniture','Office Furniture',4729.00,6857.05),(61,'Notebook 061','Stationery','Notebooks',90.00,162.00),(62,'Notebook 062','Stationery','Notebooks',109.00,196.20),(63,'Notebook 063','Stationery','Notebooks',128.00,230.40),(64,'Notebook 064','Stationery','Notebooks',147.00,264.60),(65,'Notebook 065','Stationery','Notebooks',66.00,118.80),(66,'Notebook 066','Stationery','Notebooks',85.00,153.00),(67,'Notebook 067','Stationery','Notebooks',104.00,187.20),(68,'Notebook 068','Stationery','Notebooks',123.00,221.40),(69,'Notebook 069','Stationery','Notebooks',142.00,255.60),(70,'Notebook 070','Stationery','Notebooks',61.00,109.80),(71,'Notebook 071','Stationery','Notebooks',80.00,144.00),(72,'Notebook 072','Stationery','Notebooks',99.00,178.20),(73,'Notebook 073','Stationery','Notebooks',118.00,212.40),(74,'Notebook 074','Stationery','Notebooks',137.00,246.60),(75,'Notebook 075','Stationery','Notebooks',56.00,100.80),(76,'Notebook 076','Stationery','Notebooks',75.00,135.00),(77,'Notebook 077','Stationery','Notebooks',94.00,169.20),(78,'Notebook 078','Stationery','Notebooks',113.00,203.40),(79,'Notebook 079','Stationery','Notebooks',132.00,237.60),(80,'Notebook 080','Stationery','Notebooks',51.00,91.80),(81,'Coffee Maker 081','Home Appliances','Kitchen Appliances',3680.00,5520.00),(82,'Coffee Maker 082','Home Appliances','Kitchen Appliances',3891.00,5836.50),(83,'Coffee Maker 083','Home Appliances','Kitchen Appliances',4102.00,6153.00),(84,'Coffee Maker 084','Home Appliances','Kitchen Appliances',1813.00,2719.50),(85,'Coffee Maker 085','Home Appliances','Kitchen Appliances',2024.00,3036.00),(86,'Coffee Maker 086','Home Appliances','Kitchen Appliances',2235.00,3352.50),(87,'Coffee Maker 087','Home Appliances','Kitchen Appliances',2446.00,3669.00),(88,'Coffee Maker 088','Home Appliances','Kitchen Appliances',2657.00,3985.50),(89,'Coffee Maker 089','Home Appliances','Kitchen Appliances',2868.00,4302.00),(90,'Coffee Maker 090','Home Appliances','Kitchen Appliances',3079.00,4618.50),(91,'Coffee Maker 091','Home Appliances','Kitchen Appliances',3290.00,4935.00),(92,'Coffee Maker 092','Home Appliances','Kitchen Appliances',3501.00,5251.50),(93,'Coffee Maker 093','Home Appliances','Kitchen Appliances',3712.00,5568.00),(94,'Coffee Maker 094','Home Appliances','Kitchen Appliances',3923.00,5884.50),(95,'Coffee Maker 095','Home Appliances','Kitchen Appliances',4134.00,6201.00),(96,'Coffee Maker 096','Home Appliances','Kitchen Appliances',1845.00,2767.50),(97,'Coffee Maker 097','Home Appliances','Kitchen Appliances',2056.00,3084.00),(98,'Coffee Maker 098','Home Appliances','Kitchen Appliances',2267.00,3400.50),(99,'Coffee Maker 099','Home Appliances','Kitchen Appliances',2478.00,3717.00),(100,'Coffee Maker 100','Home Appliances','Kitchen Appliances',2689.00,4033.50);
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-24 22:22:51
